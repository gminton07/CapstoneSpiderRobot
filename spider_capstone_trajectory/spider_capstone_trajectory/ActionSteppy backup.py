# packages to make it work
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import String
from sensor_msgs.msg import Joy                    # for joystick subscription
from sensor_msgs.msg import JointState             # grab leg current place
from control_msgs.srv import QueryTrajectoryState  # for  jtc feedback

# import math libraries and functions
from math import pi       # import number
import numpy as np        # import numpi library for fast math
import kdl_wrapper as kdl # ?
# functions:
from .Inverse_Kinematics import inverse_kinematic_FR, inverse_kinematic_FL, inverse_kinematic_RL, inverse_kinematic_RR
from .Rotations import walking_cycle # creates walking cycle


# import action:
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient


class ActionSteppy(Node): # nodes are class objects, what defines it
    def __init__(self): # when create class, automatically runs on class creation
        super().__init__('ActionSteppy')

        ## CLASS INSTANCE? VARIABLES ##
        self.current_point = [] # this will store the point the trajectory controller is currently sending to servo2040
        self.prevDirect = 'placeholder direction string' # this  saves the previous walking direction
        self.finished_actions = 0# to track if all for legs have finished (to walk again)
        self.debug_button_pressed = False   # A button to debug random things
        self.walk_again_counter = 0 # tells publish_trajectory () to loop again *screams in eternal code anguish*

        qos_profile = QoSProfile( #for getting xml string (robot description, recall from robotics class we used it for part 1)
            depth=1, #how deep in array
            durability=DurabilityPolicy.TRANSIENT_LOCAL, # rrquired but neil (moi) shouldnt mess with it.
            reliability=ReliabilityPolicy.RELIABLE
        )

        ## CREATE SUBSCRIPTIONS ##
        self.subscription_ = self.create_subscription( # sets up messaging
            String,                                    # message type
            '/robot_description',                      # topic name
            self.urdf_callback,                        # function to run when you recieve message
            qos_profile                                # just runs (ignore but still needed)
        )
        ## subscribe to the joy node:
        self.joy_subscription_ = self.create_subscription(
            Joy,     # I think its an array?
            '/joy',
            self.read_joystick,
            10    # how many messages can be sent at once for a topic?
        )
        ## subscribe to leg joinyt trajectory controllers (for clean state transition)
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 
            10
        )

        #### SERVICE SETUP(?) ####
        self.query_client_FR = self.create_client(QueryTrajectoryState, '/joint_trajectory_controller_1/query_state')

        #creating action client object and saving to a now created self variable
        action_client_FR = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_controller_1/follow_joint_trajectory')
        action_client_FL = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_controller_2/follow_joint_trajectory')
        action_client_BL = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_controller_3/follow_joint_trajectory')
        action_client_BR = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_controller_4/follow_joint_trajectory')
        #   can have multiple action_clients, its just a generic name.
        self.jtc_Action_Publishers = {1: action_client_FR, # for each leg, compiled here into neat dictionary
                                      2: action_client_FL, # these were declared above, 
                                      3: action_client_BL, # so we can easily loop through them
                                      4: action_client_BR} 

        # SOOOO TURNS OUT YOU STILL NEED THESE JUST TO INTERUP ACTIONS
        publisher1_ = self.create_publisher(JointTrajectory, '/joint_trajectory_controller_1/joint_trajectory',10)                                                 #depth (qos depth related thingy)
        publisher2_ = self.create_publisher(JointTrajectory, '/joint_trajectory_controller_2/joint_trajectory', 10)
        publisher3_ = self.create_publisher(JointTrajectory, '/joint_trajectory_controller_3/joint_trajectory',  10)
        publisher4_ = self.create_publisher(JointTrajectory, '/joint_trajectory_controller_4/joint_trajectory', 10)
        self.jtc_publishers = {1: publisher1_, # for each leg, compiled here into neat dictionary
                               2: publisher2_, # these were declared above, 
                               3: publisher3_, # so we can easily loop through them
                               4: publisher4_} 

        self.duration_step = .1  # how long each step should take, 
        #self.timer_ = self.create_timer(self.duration_step*20, self.publish_trajectory) # makes timer, for timing actions. 15 default
        #self.timer_ = self.create_timer(self.duration_step*20, self.publish_trajectory)
        self.get_logger().info('Joint trajectory publisher started!')                   # try number of points?

        self.walk_array_dict = {"Strafe Front":self.create_angle_array(0), #creates the path in multiple directions in a dictionary
                                "Strafe Back":self.create_angle_array(np.pi),
                                "Strafe Left":self.create_angle_array(np.pi*0.5),
                                "Strafe Right":self.create_angle_array(np.pi*-0.5),
                                "Strafe FrontLeft":self.create_angle_array(np.pi*0.25),
                                "Strafe FrontRight":self.create_angle_array(np.pi*-0.25),
                                "Strafe BackLeft":self.create_angle_array(np.pi*0.75),
                                "Strafe BackRight":self.create_angle_array(np.pi*-0.75),
                                "STOP":{1:[[0,0,0],[0,0,0]], 2:[[0,0,0],[0,0,0]],3:[[0,0,0],[0,0,0]],4:[[0,0,0],[0,0,0]]}}
        self.strafe_direction = "Strafe Front" # initial walking direction

    def urdf_callback(self, msg: JointTrajectory): #extracts names of joints from urdf tree.
        '''
        Create the Chain and extract mobile joint names for each leg
        '''

        try:
            self.tree = kdl.tree_from_xml(msg.data)
            self.get_logger().info(f'Tree created with {self.tree.getNrOfSegments()} segments')

            base_link = 'base_link'
            tip_link = 'fr_end_effector'
            tip_link = ['fr_end_effector', 'fl_end_effector', 'bl_end_effector', 'br_end_effector']

            self.chains = {}
            self.chain_names = {}

            for i in range(0,4):
                chain = self.tree.getChain(base_link, tip_link[i])

                num_joints = chain.getNrOfJoints()
                self.get_logger().info(f"Chain extracted from {base_link} to {tip_link[i]}")
                self.get_logger().info(f"Number of joints in chain: {num_joints}")

                # Get names of mobile joints
                names = get_joint_names(chain) # function is down below
                self.get_logger().info(f"Active joints in chain: {names}")

                # Add to chains dict
                self.chains[i+1] = chain
                self.chain_names[i+1] = names

            # Stop listening after data received
            self.destroy_subscription(self.subscription_)
            
        except Exception as e:
            self.get_logger().error(f"Failed to setup KDL: {str(e)}")

    def create_angle_array(self,ang_direction):
        [FL,FR,BL,BR] = walking_cycle(ang_direction) #create point loop with correct offset for each leg

        # Pull the points from the walking cycle #
        Points_FL = FL[0:3,:].T  # I believe this this strips off the extra 1?
        Points_FR = FR[0:3,:].T
        Points_BL = BL[0:3,:].T
        Points_BR = BR[0:3,:].T

        total_pts = len(Points_BR)#number of points in a path, currently hardcoded. Needed for calibration reasons below.
        point_array_FL = []
        point_array_FR = []
        point_array_BL = []
        point_array_BR = []
        for i in range(total_pts):
            theta_FL = inverse_kinematic_FL(Points_FL[(15 + i) % total_pts,:]) 
            theta_FR = inverse_kinematic_FR(Points_FR[(5 + i) % total_pts,:])
            theta_BL = inverse_kinematic_RL(Points_BL[(10 + i) % total_pts,:])
            theta_BR = inverse_kinematic_RR(Points_BR[(0 + i) % total_pts,:])
            point_array_FL.append(theta_FL)
            point_array_FR.append(theta_FR)
            point_array_BL.append(theta_BL)
            point_array_BR.append(theta_BR)
        return {1: point_array_FR, 2: point_array_FL, 3: point_array_BL, 4: point_array_BR}

    def try_catch_from_hell(self): # attemp to handle goals from all 4 legs
            try:
                self.goal_handle_FR
            except AttributeError:
                print('\033[91m'+'No current goal? ERROR' + '\033[0m')
            else:
                self.goal_handle_FR.cancel_goal_async()
                #print('\033[91m' + 'STOPPING FR' + '\033[0m')

            try:
                self.goal_handle_FL
            except AttributeError:
                print('\033[91m'+'No current goal? ERROR' + '\033[0m')
            else:
                self.goal_handle_FL.cancel_goal_async()
                #print('\033[91m' + 'STOPPING FL' + '\033[0m')

            try:
                self.goal_handle_BL
                    #self.goal_handle_FR.cancel_goal_async()
            except AttributeError:
                print('\033[91m'+'No current goal? ERROR' + '\033[0m')
            else:
                self.goal_handle_BL.cancel_goal_async()
                #print('\033[91m' + 'STOPPING BL' + '\033[0m')

            try:
                self.goal_handle_BR
                    #self.goal_handle_FR.cancel_goal_async()
            except AttributeError:
                print('\033[91m'+'No current goal? ERROR' + '\033[0m')
            else:
                self.goal_handle_BR.cancel_goal_async()
                #print('\033[91m' + 'STOPPING BR' + '\033[0m')
    
    
    def request_current_state(self): ## needed for requesting joint position, might not use this method.
        req = QueryTrajectoryState.Request() # make the request object
        # Request state for timestamp: self.get_clock().now() gets current time. I think .msg converts to a format?
        req.time = self.get_clock().now().to_msg()
        response_obj = self.query_client_FR.call_async(req) # somethim something mailbox?
        response_obj.add_done_callback(self.response_callback_FR) # send mail to this function
    
    def response_callback_FR(self, future): ## prepared/used for/by request_current_state
        response = future.result()
        #print(response)#.actual.positions)
        print('AAAAAAAAAAAAAAAAAAAAAAA')
        print(response)

    def read_joystick(self, msg): # axes is defined in msg for joy subscriber,
        if msg.buttons[0] == 1 and self.debug_button_pressed == False: # the "testing things" button
            self.debug_button_pressed = True
            print("debug button pressed")
            self.transition_trajectory() # begin transitioning to next state
            self.request_current_state() # DEBUG -- seeing if transition_trajectory is using the right points
        elif msg.buttons[0] == 0 and self.debug_button_pressed == True:
            self.debug_button_pressed = False
            print("debug button released")

        joy_mag      = np.sqrt(msg.axes[1]**2 + msg.axes[0]**2)
        if joy_mag > 0.8:
            joy_left_ang = np.arctan2(msg.axes[0],msg.axes[1]) + np.pi #the pi makes it go from 0->2pi
            #print(f'{joy_left_ang} mag: {joy_mag}')
        # think in 8 chunks?
            if joy_left_ang >= 5.75:
                self.strafe_direction = "Strafe Back"
            elif joy_left_ang >= 5.2:
                self.strafe_direction = "Strafe BackLeft"
            elif joy_left_ang >= 4.2:
                self.strafe_direction = "Strafe Left"
            elif joy_left_ang >= 3.65:
                self.strafe_direction = "Strafe FrontLeft"
            elif joy_left_ang >= 2.6:
                self.strafe_direction = "Strafe Front"
            elif joy_left_ang >= 2.1:
                self.strafe_direction = "Strafe FrontRight"
            elif joy_left_ang >= 1.1: 
                self.strafe_direction = "Strafe Right"
            elif joy_left_ang >= 0.5:
                self.strafe_direction = "Strafe BackRight"
            elif joy_left_ang >= 0.0:
                self.strafe_direction = "Strafe Back" # could have put in else,
            else:
                print("a joystick direction error, somehow") # should be mathmatically impossible to get here

            if self.prevDirect != self.strafe_direction: # only print this on change
                self.prevDirect = self.strafe_direction
                print('\033[32m' + f'set direc to: {self.strafe_direction}' + '\033[0m')
                self.try_catch_from_hell() # stop legs current goal
                #self.publish_trajectory() # Basically "update on change" IDEA, INSTEAD OF UPDATE, TRANSITION -> UPDATE!!
                self.transition_trajectory()

        else: #joystick is not pushed, robot should stop
            if self.current_point != [] and self.strafe_direction != "STOP":
                self.strafe_direction = "STOP" # NOTE as of 4/1/2026 this state should NEVER be published to JCTs, just used in logic.
                self.prevDirect = self.strafe_direction
                print('\033[91m' + 'STOPPING STATE' + '\033[0m')
                self.try_catch_from_hell() # stops the legs from walking. "pause".
                #self.publish_trajectory()
                #self.request_current_state() # for "resquest current state" testing. unused as of 4/6/2026 
                #self.transition_trajectory() # begin transition to next state
                

    def joint_state_callback(self, msg: JointState): # INTERESTING gives message of all 4 leg positions with timestamp
        self.current_point = msg # basically just a status update of allk 4 jtcs at the same time.
        #print(f'bl: {msg.name[0:3]}, {msg.position[0:3]},')
        #print(f'bl: {msg.name}, {msg.position},')
        #print(f'timestamp: {msg.Time}') # trying to get time stamp of last point. (the one we sent it)
        #self.transition_trajectory(msg)


    # def send_pathgoals(self):
    #     goal_FR_msg = FollowJointTrajectory.Goal() #creates an instance goal object for a generic FollowJointTrajectory action
    #                                                # does not know anthing, think of as blank clipboard
    #     point =  JointTrajectoryPoint()# the goal clipboard will need a list of points, we shal create a generic "point" object
    #     point.positions = [.4,.4,.4] 
    #     point.time_from_start = Duration(seconds=10, nanoseconds=0).to_msg() # time stamp for single point

    #     goal_FR_msg.trajectory.joint_names = self.chain_names[1] # tell clipboard what the joints are
    #     goal_FR_msg.trajectory.points = [point]                  # attach point array (in order?) to clipboard 

    #     #self.action_client_FR.wait_for_server() #???
    #     self.action_client_FR.send_goal_async(goal_FR_msg) # shove this into print statement?
    #     return 


    def publish_trajectory(self,trans_time):
        if not self.chains: # stops the chain error
            return
        # print(self.chain_names)
        if self.strafe_direction == "STOP":
            print("aborted erronious walk")
            return # if in stop staste, dont try to walk.

        self.get_logger().info('publish_trajectory') # send logger message (shows up in terminal for debugging)
                        # logger means print to consol here
        ## Create the JointTrajectory message
        goal_FR_msg = FollowJointTrajectory.Goal()
        goal_FL_msg = FollowJointTrajectory.Goal() 
        goal_BL_msg = FollowJointTrajectory.Goal()
        goal_BR_msg = FollowJointTrajectory.Goal() # creates an object of jointTrajectory Message type
        self.goal_msgs = {1: goal_FR_msg, 2: goal_FL_msg, 3: goal_BL_msg, 4: goal_BR_msg} #array became disctonary :D
        
        # for i in goal_msgs: # honest no clue whatthis is for, does not crash if I comment it out.
        #     goal_msgs[i].header.stamp = self.get_clock().now().to_msg() # timestamps message
        #     goal_msgs[i].header.frame_id = 'base_link' # its an id, has to be here

        ## Append points to trajectory
        print(f'walking with: -{self.strafe_direction}- point array')
        for j in range(1, 4+1):
            point_duration = trans_time # how long a step takes, trans_time gives time for the transition to complete
            #msg.points = [] # resets points so messages dont contaminate each other
            first_pt = self.walk_array_dict[self.strafe_direction][j][0]
            for points in self.walk_array_dict[self.strafe_direction][j]: #point_array: # only runs once, part of set up. (packages each point for message sendoff)
                point = JointTrajectoryPoint()  ## note/\ every other array index starts at 1 (why?), the j-1 is because point_4leg_array starts at 0
                point.positions = points
                point.time_from_start = Duration(seconds=point_duration).to_msg() #adds how much time it takes to get to point.
                point_duration += self.duration_step
                self.goal_msgs[j].trajectory.points.append(point) #adds points to end of message, msg gets overwritten every time.
            reset_pt = JointTrajectoryPoint()  ## note/\ every other array index starts at 1 (why?), the j-1 is because point_4leg_array starts at 0
            reset_pt.positions = first_pt
            reset_pt.time_from_start = Duration(seconds=point_duration).to_msg() #adds how much time it takes to get to point.
            self.goal_msgs[j].trajectory.points.append(reset_pt) # goes back to first point
            
            ## Publish JointTrajectory message, ### 1 is FR, 2>FL, 3>BL, 4>BR
            #for i in range(1, 4+1): # loop takes joint names (stored chain names)
            self.goal_msgs[j].trajectory.joint_names = self.chain_names[j] # for like angle 1 gets asssigned to joint *_sholder and such.
            #self.jtc_publishers[j].publish(msg[j]) # what sends out the message neil added i here.
            #self.get_logger().info(f'Published joint trajectory to controller {j}. Points: {len(goal_msgs[j].trajectory.points)}')
        future_FR = self.jtc_Action_Publishers[1].send_goal_async(self.goal_msgs[1])  ## this sends goal and creates a response variable
        future_FL = self.jtc_Action_Publishers[2].send_goal_async(self.goal_msgs[2])
        future_BL = self.jtc_Action_Publishers[3].send_goal_async(self.goal_msgs[3])
        future_BR = self.jtc_Action_Publishers[4].send_goal_async(self.goal_msgs[4])
        future_FR.add_done_callback(self.on_FR_callback) # tell response variable thing to call function when action recieved
        future_FL.add_done_callback(self.on_FL_callback)
        future_BL.add_done_callback(self.on_BL_callback)
        future_BR.add_done_callback(self.on_BR_callback)



    def transition_trajectory(self): # basically publish_trajectory() but with custom points to transition between states
        #self.get_logger().info('publish_transition_trajectory') # send logger message (shows up in terminal for debugging)
        #print("BEGIN TRANSITION")
        goal_FR_msg = FollowJointTrajectory.Goal() # creates an object of jointTrajectory Message type
        goal_FL_msg = FollowJointTrajectory.Goal() 
        goal_BL_msg = FollowJointTrajectory.Goal()
        goal_BR_msg = FollowJointTrajectory.Goal() 
        self.goal_msgs = {1: goal_FR_msg, 2: goal_FL_msg, 3: goal_BL_msg, 4: goal_BR_msg} #array became disctonary :D
 
        first_points = [9999,9999,9999,9999] # creates 4 slots to be overwritten
        for j in range(1, 4+1): # prep the end of the transition
            point_duration = 3.0 # 3 angles, duragtion. This tells how long travel time should take. (we guess this)
            #msg.points = [] # resets points so messages dont contaminate each other
            first_points[j-1] = self.walk_array_dict[self.strafe_direction][j][0] # grab first point of each leg's walk path

        ## TRAN FR:
        for r in range(1, 4+1):
            # reset point (overwrites last action in jtc if one is there) (not sure if thats how jtc works with 0.0 pts?)
            point = JointTrajectoryPoint()  ## note/\ every other array index starts at 1 (why?), the j-1 is because point_4leg_array starts at 0
            point.positions = [self.current_point.position[10], self.current_point.position[11], self.current_point.position[9]]
            point.time_from_start = Duration(seconds=0.1).to_msg() # logic says this should be 0, 1 works though???
            self.goal_msgs[r].trajectory.points.append(point) 

            # raise up in the air to not drag
            point = JointTrajectoryPoint()  ## note/\ every other array index starts at 1 (why?), the j-1 is because point_4leg_array starts at 0
            point.positions = np.array(first_points[r-1]) + np.array([0, 2, 0]) # just raises into air slightly
            #print(point.positions)
            point.time_from_start = Duration(seconds=1).to_msg() #adds how much time it takes to get to point.
            self.goal_msgs[r].trajectory.points.append(point)

            # go to start point of next cycle
            point = JointTrajectoryPoint()  ## note/\ every other array index starts at 1 (why?), the j-1 is because point_4leg_array starts at 0
            point.positions = first_points[r-1]
            point.time_from_start = Duration(seconds=1.5).to_msg() #adds how much time it takes to get to point.
            self.goal_msgs[r].trajectory.points.append(point)
            self.goal_msgs[r].trajectory.joint_names = self.chain_names[r] # finally attach chain names
            self.jtc_Action_Publishers[r].send_goal_async(self.goal_msgs[r])
        #print("TRANSITION sent") 
        #(f"from transition: {point.positions}")
        ###### WAIT NEED TO ADDD TRANSITION WAIT TIME SO IT DOSNT GET OVERWRITTEN
        self.publish_trajectory(2.0) # after transition now move to next part

    # this strategy of chaining functions appears to be manditory... WHY!?
    def on_step_response_callback(self, future): # ACTIVATES WHEN ACTION SENT,
        self.throw_error # this will crash program as intended.
        #print(f'action sent, launch info: {future.result().accepted}, Status={future.result().status}') # just .result
        goal_handle = future.result()   ## NOTE from future  create a goal_handel object !!!!!
        get_result_future = goal_handle.get_result_async()  # ask for result when finished 
        get_result_future.add_done_callback(self.on_step_finish_callback) # when finished send result here?
        goal_handel.action_name

        #goal_handle.cancel_goal_async()


    # FK IT WERE MAKING 4 OF THEM... WHY IS THERE NO CLEAR DOCUMENTATION OF WHAT A GOAL HANDLLE OBJECT THNGY IS FOR JUST JTC?
    def on_FR_callback(self, future): # ACTIVATES WHEN ACTION SENT,
        #print(f'action sent, launch info: {future.result().accepted}, Status={future.result().status}') # just .result
        goal_handle = future.result()   ## NOTE from future  create a goal_handel object !!!!!
        get_result_future = goal_handle.get_result_async()  # ask for result when finished 
        get_result_future.add_done_callback(self.on_step_finish_callback) # when finished send result here?
        self.goal_handle_FR = goal_handle
    
    def on_FL_callback(self, future): # ACTIVATES WHEN ACTION SENT,
        #print(f'action sent, launch info: {future.result().accepted}, Status={future.result().status}') # just .result
        goal_handle = future.result()   ## NOTE from future  create a goal_handel object !!!!!
        get_result_future = goal_handle.get_result_async()  # ask for result when finished 
        get_result_future.add_done_callback(self.on_step_finish_callback) # when finished send result here?
        self.goal_handle_FL = goal_handle
    
    def on_BL_callback(self, future): # ACTIVATES WHEN ACTION SENT,
        #print(f'action sent, launch info: {future.result().accepted}, Status={future.result().status}') # just .result
        goal_handle = future.result()   ## NOTE from future create a goal_handel object !!!!!
        get_result_future = goal_handle.get_result_async()  # ask for result when finished 
        get_result_future.add_done_callback(self.on_step_finish_callback) # when finished send result here?
        self.goal_handle_BL = goal_handle

    def on_BR_callback(self, future): # ACTIVATES WHEN ACTION SENT,
        #print(f'action sent, launch info: {future.result().accepted}, Status={future.result().status}') # just .result
        goal_handle = future.result()   ## NOTE from future  create a goal_handel object !!!!!
        get_result_future = goal_handle.get_result_async()  # ask for result when finished 
        get_result_future.add_done_callback(self.on_step_finish_callback) # when finished send result here?
        self.goal_handle_BR = goal_handle



    def on_step_finish_callback(self, future):  # ACTIVATES WHEN ACTION just FINISHED
        #print("action completed??")
        # #print(f'Completed goal? {future.status}')
        #print(f'end result: {future.result().result}') # just .result
        if future.result().result.error_string == '':
            #print('leg interrupted')   debug print statment, leave in plz
            pass
        elif future.result().result.error_string == 'Goal successfully reached!':
            # print('leg finished')
            # print('+1')
            self.walk_again_counter = self.walk_again_counter + 1
        else:
            print(future.result().result) # basically an error check, should never go here unless something is very wrong
        if self.walk_again_counter >= 4: # if all 4 legs finished walking, walk again.
            print(f'step again! counter = {self.walk_again_counter}')
            self.walk_again_counter = 0
            self.publish_trajectory(0)



        # # Code for restarting the walking when a step finished:
        # self.finished_actions = self.finished_actions + 1
        # if self.finished_actions == 3: #  verify all 4 legs finished
        #     self.finished_actions = 0
        #     self.publish_trajectory()
        # elif self.finished_actions > 3: # complain if we somehow counted more
        #     print(f'how heck did it get {self.finished_actions}?')
        # else: # counts the legs, seriously WHY DO GOAL/FUTURE OBJECTS LACK NAME IDENTIFIRES, NO THE ID VALUE IS INSTANCE UNIQUE
        #     print(f'counting, {self.finished_actions}')



# GENERIC FUNCTIONS  (not part of class but may be used by instances)
def get_joint_names(chain): #kdl wrapper library (kinmatics and dynamics)
    joint_names = []        # just gets names of MOVEABLE joints
    # Loop through every segment in the chain
    for i in range(chain.getNrOfSegments()):
        segment = chain.getSegment(i)
        joint = segment.getJoint()
        
        # KDL::Joint::None represents a fixed connection (0 DOF)
        # We usually only want 'Revolute' or 'Prismatic' joints
        if joint.getTypeName() not in ["None", "Fixed"]:
            joint_names.append(joint.getName())
            #print(f'{joint.getName()}: {joint.getTypeName()}')
            
    return joint_names






# always need a main!
def main(): # makes object and spins up node
    rclpy.init()
    node = ActionSteppy() # while in the spin (state?) I think BigSteppy() acts as main loop?
    rclpy.spin(node) # neil note: I think the node exists here until you hit ctrl^c or otherwise terminate node.
    node.destroy_node()
    rclpy.shutdown()

# technically this is executed first if you think about it.
if __name__ == '__main__':
    main()

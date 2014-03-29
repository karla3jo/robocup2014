#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat March 16 11:30:00 2013

@author: Chang Long Zhu
@email: changlongzj@gmail.com
"""


import rospy
import smach
from navigation_states.nav_to_coord import nav_to_coord
from navigation_states.nav_to_poi import nav_to_poi
from navigation_states.enter_room import EnterRoomSM
from speech_states.say import text_to_say
from manipulation_states.play_motion_sm import play_motion_sm
from util_states.topic_reader import topic_reader
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped

# Some color codes for prints, from http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
ENDC = '\033[0m'
FAIL = '\033[91m'
OKGREEN = '\033[92m'

import random

class DummyStateMachine(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeeded','aborted', 'preempted'], 
            input_keys=[], 
            output_keys=['nav_to_poi_name']) #todo: i have to delate de output_key

    def execute(self, userdata):
        print "Dummy state just to change to other state"  # Don't use prints, use rospy.logXXXX

        rospy.sleep(1)
        return 'succeeded'

# Class that prepare the value need for nav_to_poi
class prepare_poi_person_emergency(smach.State):
    def __init__(self):
         smach.State.__init__(self, outcomes=['succeeded','aborted', 'preempted'], 
            input_keys=['person_location'], 
            output_keys=['nav_to_poi_name']) 

    def execute(self,userdata, poi_type='arena_door_out'):
        userdata.nav_to_poi_name = userdata.person_location

        return 'succeeded'

class prepare_tts(smach.State):
    def __init__(self, tts_text_phrase):
        smach.State.__init__(self, 
            outcomes=['succeeded','aborted', 'preempted'], 
            output_keys=['tts_text']) 
        self.tts_text_phrase_in = tts_text_phrase
    def execute(self, userdata):
        userdata.tts_text = self.tts_text_phrase_in

        return 'succeeded'


class Save_People_Emergency(smach.StateMachine):
    """
    Executes a SM that does the Emergency Situation's Save People SM.
    It is a SuperStateMachine (contains submachines) with these functionalities (draft):
    1. Go to Person location
    2. Ask Status
    3. Register position
    4. Save info
    What to do if fail?

    Required parameters:
    No parameters.

    Optional parameters:
    No optional parameters

    Input_keys:
    @key: emergency_person_location: person's location (Geometry or PoseStamped)

    Output Keys:
        none
    No io_keys.

    Nothing must be taken into account to use this SM.
    """
    def __init__(self):
        smach.StateMachine.__init__(self, ['succeeded', 'preempted', 'aborted'],
                                    input_keys=['person_location'])

        with self:           
            self.userdata.emergency_location = []
            self.userdata.tts_lang = 'en_US'
            self.userdata.tts_wait_before_speaking = 0
            smach.StateMachine.add(
                'Prepare_Say_Rescue',
                prepare_tts('I am going to rescue you!'),
                transitions={'succeeded':'Say_Rescue', 'aborted':'Say_Rescue', 'preempted':'Say_Rescue'})
            smach.StateMachine.add(
                'Say_Rescue',
                text_to_say(),
                transitions={'succeeded':'Prepare_Go_To_Person', 'aborted':'Prepare_Go_To_Person', 'preempted':'Prepare_Go_To_Person'})

            smach.StateMachine.add(
                'Prepare_Go_To_Person',
                prepare_poi_person_emergency(),
                transitions={'succeeded':'Go_To_Person', 'aborted':'Go_To_Person', 'preempted':'Go_To_Person'})
            smach.StateMachine.add(
                'Go_To_Person',
                DummyStateMachine(),
                #nav_to_poi(),
                transitions={'succeeded':'Prepare_Ask_Status', 'aborted':'Prepare_Ask_Status', 'preempted':'Prepare_Ask_Status'})

            #It should be Speech Recognition: ListenTo(?)
            smach.StateMachine.add(
                'Prepare_Ask_Status',
                prepare_tts('Are you Ok?'),
                transitions={'succeeded':'Ask_Status', 'aborted':'Ask_Status', 'preempted':'Ask_Status'})
            smach.StateMachine.add(
                'Ask_Status',
                text_to_say(),
                transitions={'succeeded':'Register_Position', 'aborted':'Register_Position', 'preempted':'Register_Position'})

            #Register Position --> TODO? or done?
            #Output keys: topic_output_msg & standard_error
            #amcl_pose : PoseWithCovarianceStamped()
            #TODO: At the moment /amcl_pose in gazebo is not working properly
            self.userdata.position_stamped = PoseWithCovarianceStamped()

            smach.StateMachine.add(
                'Register_Position',
                DummyStateMachine(),
                #topic_reader('/amcl_pose', PoseWithCovarianceStamped, 30),
                transitions={'succeeded':'Save_Info', 'aborted':'Save_Info', 'preempted':'Save_Info'}
                #remapping={'topic_output_msg':'position_stamped', 'standard_error':'standard_error'}
                )
            #Save_Info(): Saves the emergency info and generates a pdf file
            #input_keys: position_stamped

            smach.StateMachine.add(
                'Save_Info',
                DummyStateMachine(),
                transitions={'succeeded':'succeeded', 'aborted':'aborted', 'preempted':'preempted'})
            
#! /usr/bin/env python

import rospy

from pal_interaction_msgs.msg import ASRSrvRequest, ASRSrvResponse, ASREvent, ASRActivation, ASRGrammarMngmt, ASRLanguage, actiontag
from pal_interaction_msgs.srv import ASRService, ASRServiceRequest, ASRServiceResponse


MOCK_SAID = "what is the capital of spain"

class AsrService():
    """ASR Mock service 
        
        This mock service will simulate reem hearing  someone saying MOCK_SAID
        also simulate grammar analysis of what it hearint [bring] & [coke]   on line 88 (if want to change modifie there)
        
        exemple of using tags in pyton:
        
        def take_order_cb(userdata, message):
                self.last_drink_name = None
                print colors.BACKGROUND_GREEN, "MESSAGE: ", str(message), colors.NATIVE_COLOR

                actiontag = [tag for tag in message.tags if tag.key == 'action']
                drinktag = [tag for tag in message.tags if tag.key == 'object']  # drink
                if actiontag and actiontag[0].value == 'bring':
                    print "\n\nDRINK TAG: ", drinktag
                    userdata.out_drink_order = DrinkOrder(userdata.in_person_name, drinktag[0].value)
                    self.last_drink_name = drinktag[0].value
                    rospy.loginfo("==========>>> New drink: (%s, %s)" % (userdata.in_person_name, drinktag[0].value))
                    return succeeded
                return aborted
    
    """
    
    def __init__(self):
        rospy.loginfo("Initializing asrservice")
        self.enabled_asr = False
        self.current_grammar = ""
        self.enabled_grammar = False
        self.current_lang = ""
        self.asrservice = rospy.Service('/asr_server', ASRService, self.asr_grammar_cb)
        rospy.loginfo("asr service initialized")
        self.usersaid_pub = rospy.Publisher('/asr_event', ASREvent)
        
    def asr_grammar_cb(self, req):
        """Callback of asr service requests """
        #req = ASRServiceRequest() # trick to autocomplete
        resp = ASRServiceResponse()
        for curr_req in req.request.requests:
            rospy.loginfo("In the for loop")
            if curr_req == req.request.ACTIVATION:
                if req.request.activation.action == ASRActivation.ACTIVATE:
                    self.enabled_asr = True
                    rospy.loginfo("ASR: Enabling speech recognizer")
                if req.request.activation.action == ASRActivation.DEACTIVATE:
                    self.enabled_asr = False
                    rospy.loginfo("ASR: Disabling speech recognizer")
#                 if req.request.activation.action == ASRActivation.PAUSE:
#                     self.enabled_asr = False
#                     rospy.loginfo("ASR: Pausing speech recognizer")
#                 if req.request.activation.action == ASRActivation.RESUME:
#                     self.enabled_asr = True
#                     rospy.loginfo("ASR: Resuming speech recognizer")
                    
            elif curr_req == req.request.GRAMMAR:
                if req.request.grammar.action == ASRGrammarMngmt.ENABLE:
                    self.enabled_grammar = True
                    self.current_grammar = req.request.grammar.grammarName
                    rospy.loginfo("ASR: Enabling grammar '%s'" % req.request.grammar.grammarName)
                if req.request.grammar.action == ASRGrammarMngmt.DISABLE:
                    self.enabled_grammar = False
                    self.current_grammar = ""
                    rospy.loginfo("ASR: Disabling grammar")
#                 if req.request.grammar.action == ASRGrammarMngmt.LOAD:
#                     self.current_grammar = req.request.grammar.grammarName
#                     rospy.loginfo("ASR: Loading grammar '%s'" % ASRGrammarMngmt.grammarName)
#                 if req.request.grammar.action == ASRGrammarMngmt.UNLOAD:
#                     self.current_grammar = ""
#                     rospy.loginfo("ASR: Unloading grammar")
                    
            elif curr_req == req.request.LANGUAGE:
                self.current_lang = req.request.lang.language
                rospy.loginfo("ASR: Changing lang to: '%s'" % req.request.lang.language)
                
            #elif curr_req == ASRServiceRequest.request.STATUS: # always return status
            
            resp.response.status.active = self.enabled_asr
            resp.response.status.enabled_grammar = self.current_grammar
            resp.response.status.language = self.current_lang
            resp.response.error_msg = ""
            resp.response.warn_msg = ""
                            
        return resp
                 
        
    def run(self):
        """Publishing usersaid when grammar is enabled """
        # TODO: add tags, add other fields, take into account loaded grammar to put other text in the recognized sentence
        while not rospy.is_shutdown():
            if self.enabled_asr and self.enabled_grammar:
                recognized_sentence = ASREvent()
                recognized_sentence.recognized_utterance.text = MOCK_SAID
                recognized_sentence.recognized_utterance.confidence = recognized_sentence.recognized_utterance.CONFIDENCE_MAX
                #recognized_sentence.recognized_utterance.tags = []
                tag = actiontag()
                tag.key = 'info'
                tag.value = 'president'
                recognized_sentence.recognized_utterance.tags.append(tag);
                tag = actiontag()
                tag.key = 'country'
                tag.value = 'spain'
                recognized_sentence.recognized_utterance.tags.append(tag);
                recognized_sentence.active = self.enabled_asr
                # TODO: #recognized_sentence.recognized_utterance.tags #bla bla bla
                self.usersaid_pub.publish(recognized_sentence)
            rospy.sleep(1)
        
        
                
if __name__ == '__main__':
    rospy.init_node('asr_srv')
    rospy.loginfo("Initializing asr_srv")
    asr = AsrService()
    asr.run()
  

# vim: expandtab ts=4 sw=4

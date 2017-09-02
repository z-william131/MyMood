from __future__ import print_function
import requests


url = "https://v5idpy1vl3.execute-api.us-east-1.amazonaws.com/prod/emoteDBUpdate?TableName=emote"


def lambda_handler(event, context):

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'], event['request']['timestamp'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return welcome_response()


def on_intent(intent_request, session, time):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # for starting stage
    if intent_name == "GuideIntent":
        return Guide(intent, session)
    elif intent_name == "QuitIntent":
        return Quit(intent, session)
    elif intent_name == "HowItWorks":
        return HowItWorks(intent, session)

    # for Access rocord stage
    elif intent_name == "AccessRecordIntent":
        return AccessRecord(intent, session)
    elif intent_name == "CheckTimePeriodIntent":
        return CheckTimePeriod(intent, session, time)

    elif intent_name =="AddNewIntent":
        return AddNew(intent, session)
    elif intent_name =="AddMoodIntent":
        return AddMood(intent, session, time)
    elif intent_name =="AddActivityIntent":
        return AddActivity(intent, session)
    elif intent_name =="DontKnowIntent":
        return DontKnow(intent, session)

    elif intent_name == "AMAZON.YesIntent":
        return Yesss(intent, session)
    elif intent_name == "AMAZON.NoIntent":
        return Nooo(intent, session)


    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------

def welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    session_attributes['stage'] = 'Start'
    card_title = "Online and Ready to Help"
    speech_output = "Hey William! Welcome to My Mood. Do you wanna access previous records, or add something new?"
    reprompt_text = "You can response by saying 'access previous records' or 'add something new'."
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



# functions for starting stage

def Guide(intent, session):

    session_attributes = session['attributes']

    if session_attributes['stage'] == 'Start':
        card_title = "Commands"
        speech_output = "You can give following commands: " \
                            "Access previous records. " \
                            "Add something new. " \
                            "How does it work. " \
                            "Exit. "

    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

def Quit(intent, session):

    session_attributes = session['attributes']

    if session_attributes['stage'] == 'Start':
        card_title = 'Goodbye'
        speech_output = 'Thanks for using the My Mood. Hope you have a wonderful day. Goodbye.'
        reprompt_text = ''
        should_end_session = True
        return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))

    else:
        return welcome_response()

def HowItWorks(intent, session):
    session_attributes = {}
    session_attributes = session["attributes"]
    card_title = "How it works"
    speech_output = "This application use circumplex model developped by James Russell to evaluate your mood. " \
                    "The emotions can be described by two dimensions: " \
                    "pleasurable versus unpleasurable, activation versus disactivation. "
    reprompt_text = speech_output
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# functions for access record stage

def AccessRecord(intent, session):
    session_attributes = {}
    session_attributes['stage'] = 'AccessRecord'
    card_title = 'AccessRecord'
    should_end_session = False
    speech_output = "Right on! What time period do you want to look at?"
    reprompt_text = speech_output

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def CheckTimePeriod(intent, session, time):


    session_attributes = session['attributes']
    card_title = 'CheckTimePeriod'
    should_end_session = False

    if session_attributes['stage'] == 'AccessRecord' and 'value' in intent['slots']['date']:
        date = intent['slots']['date']['value']

        request = requests.get(url)
        jsonRequest = request.json()
        items = jsonRequest["Items"]

        positiveActive = 0
        negativeActive = 0
        positiveDeactive = 0
        negativeDeactive = 0

        month = {"01":"January", "02":"February", "03":"March", "04":"April", "05":"May", "06":"June",
                 "07":"July", "08":"Auguest", "09":"September", "10":"October", "11":"November", "12":"December"}

        emotions = ["Depressed", "Excited", "Happy", "Relaxed", "Sad", "Shocked", "Stressed", "Tired", "Others"]

        activities = {}


        if len(date) == 4 and date.isdigit():
            start = date + "-01-01"
            end = str(int(date) + 1).zfill(2)  + "-01-01"
        elif len(date) == 7 and date[:4].isdigit() and date[5:7].isdigit():
            start = date + "-01"
            if date[5:7] == "12":
                end = str(int(date[:4]) + 1).zfill(2)  + "-01-01"
            elif date[5:7] == "11":
                end = str(int(date[:4]) + 1).zfill(2)  + "-01-01"
            else:
                end = date[:5] + str(int(date[5:7]) + 1).zfill(2)  + "-01"
        elif len(date) == 10 and date[:4].isdigit() and date[5:7].isdigit() and date[8:10].isdigit():

            speech_output = "Here are the entries for " + month[date[5:7]] + " " + date[8:10] + " " + date[:4] + ": "
            count = 0
            for item in items:
                if item["Date"] == date:
                    speech_output = speech_output + "time " + item["Time"] + " activity " + item["Activity"] + " mood " + emotions[int(item["MoodID"])-1] + ". "
                    count += 1

            if count == 0:
                speech_output = "Sorry. No record in that date. Please try another one."

            reprompt_text = speech_output
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))
        else:
            speech_output = "Sorry. I don't understand. Please try words like yesterday, April or 2017 April 10."
            reprompt_text = speech_output
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))



        for item in items:
            if item["Date"] >= start and item["Date"] < end:
                if item["MoodID"] == "2" or item["MoodID"] == "3":
                    positiveActive += 1
                if item["MoodID"] == "6" or item["MoodID"] == "7":
                    negativeActive += 1
                if item["MoodID"] == "4":
                    positiveDeactive += 1
                if item["MoodID"] == "1" or item["MoodID"] == "5" or item["MoodID"] == "8":
                    negativeDeactive += 1

                activity = item["Activity"]
                if activity in activities:
                    activities[activity] += 1
                else:
                    activities[activity] = 1



        maxValue = 0
        actName = "None"
        for act, num in activities.iteritems():
            if num > maxValue:
                maxValue = num
                actName = act

        if maxValue == 0:
            speech_output = "Sorry. No record in that period of time. Please try another one."
        else:
            session_attributes['stage'] = 'AccessActivity'

            session_attributes["activity"] = actName

            maxValue = max(positiveDeactive, positiveActive, negativeActive, negativeDeactive)
            if maxValue == positiveActive:
                session_attributes["emotion"] = "energized-pleasant"
            if maxValue == positiveDeactive:
                session_attributes["emotion"] = "calm-pleasant"
            if maxValue == negativeActive:
                session_attributes["emotion"] = "energized-unpleasant"
            if maxValue == negativeDeactive:
                session_attributes["emotion"] = "calm-unpleasant"

            fromDate = start[:4] + " " + month[start[5:7]] + " " + start[8:10]
            toDate = end[:4] + " " + month[end[5:7]] + " " + end[8:10]

            speech_output = ("From " + fromDate + " to " + toDate + ", you were energized-pleasant " +
                         str(positiveActive) + " times, energized-unpleasant " +
                         str(negativeActive) + " times, calm-pleasant " +
                         str(positiveDeactive) + " times, calm-unpleasant " +
                         str(negativeDeactive) + " times. Shall we look at activities? ")

    elif session_attributes['stage'] == 'AddNew' and 'value' in intent['slots']['date']:
        date = intent['slots']['date']['value']

        if len(date) == 10 and date[:4].isdigit() and date[5:7].isdigit() and date[8:10].isdigit():
            if date[:10] == time[:10]:
                session_attributes['NewTime'] = time[11:16]
            else:
                session_attributes['NewTime'] = "00:00"

            session_attributes['NewDate'] = date
            session_attributes['stage'] = "AddTime"
            speech_output = "Okay! How are you feeling?"

        else:
            speech_output = "Sorry. I don't understand. Please try again or ask what can I say."
    else:
        speech_output = "Sorry. I don't understand. Please try again or ask what can I say."

    reprompt_text = speech_output
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def AddNew(intent, session):
    session_attributes = {}
    session_attributes['stage'] = 'AddNew'
    card_title = 'AddNew'
    should_end_session = False
    speech_output = "Sweet! What is the date you want to record an entry for?"
    reprompt_text = speech_output

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def AddMood(intent, session, time):
    if session['attributes'] == {}:
        session_attributes['stage'] == 'AddTime'
        session_attributes['NewTime'] = time[11:16]
        session_attributes['NewDate'] = time[:10]

    else:
        session_attributes = session['attributes']
    card_title = 'AddMood'
    should_end_session = False

    if session_attributes['stage'] == 'AddTime' and 'value' in intent['slots']['mood']:
        mood = intent['slots']['mood']['value']

        if mood == "happy":
            speech_output = "Wow! I feel happy for you too. "
            session_attributes['NewMoodID'] = "3"
        elif mood == "excited":
            speech_output = "That's great! Always keep that energy."
            session_attributes['NewMoodID'] = "2"
        elif mood == "shocked":
            speech_output = "Time to get some more work."
            session_attributes['NewMoodID'] = "6"
        elif mood == "Stressed":
            speech_output = "You need to get some rest."
            session_attributes['NewMoodID'] = "7"
        elif mood == "sad":
            speech_output = "Cheer up! It will get better."
            session_attributes['NewMoodID'] = "5"
        elif mood == "depressed":
            speech_output = "I wish I can give you a hug."
            session_attributes['NewMoodID'] = "1"
        elif mood == "tired":
            speech_output = "Have you heard a song called river flows in you? You will feel better after listening that."
            session_attributes['NewMoodID'] = "8"
        elif mood == "relaxed":
            speech_output = "Sounds Great!"
            session_attributes['NewMoodID'] = "4"
        else:
            speech_output = "Did you say " + mood + " ?"
            reprompt_text = speech_output
            session_attributes['NewMoodID'] = "9"
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))

        speech_output += " What activity made you feel " + mood + " ?"
        session_attributes['stage'] = 'AddMood'


    else:
        speech_output = "Sorry. I don't understand. Please try again or ask what can I say."

    reprompt_text = speech_output

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def AddActivity(intent, session):
    session_attributes = session['attributes']
    card_title = 'AddActivity'
    should_end_session = False

    if session_attributes['stage'] == 'AddMood' and 'value' in intent['slots']['activity']:
        activity = intent['slots']['activity']['value']

        if activity == "study":
            actID = 1
        elif activity == "work":
            actID = 2
        elif activity == "cook":
            actID = 3
        elif activity == "photography":
            actID = 4
        elif activity == "gym":
            actID = 5
        elif activity == "social":
            actID = 6
        elif activity == "gaming":
            actID = 7
        elif activity == "date":
            actID = 8
        else:
            actID = 9

        actName = activity
        moodID = session_attributes["NewMoodID"]
        date = session_attributes["NewDate"]
        time = session_attributes["NewTime"]

        writeEntry(moodID, actName, actID, date, time)

        speech_output = "Your new entry has been saved. Have a great rest of your day."
        session_attributes["stage"] = "start"
    else:
        speech_output = "Sorry. I don't understand. Please try again or ask what can I say."

    reprompt_text = speech_output
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def DontKnow(intent, session):
    session_attributes = session['attributes']
    card_title = 'DontKnow'
    should_end_session = False

    if session_attributes["stage"] == 'AddTime':
        speech_output = "That is okay. We prepare a set of questions to help you figure out what your mood is. Let's start. Do you feel happy today?"
        session_attributes["stage"] = "IDK"
    else:
        speech_output = "Sorry. I don't understand. Please try again or ask 'what can I say'."

    reprompt_text = speech_output
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# functions for yes/no

def Yesss(intent, session):
    session_attributes = session['attributes']
    card_title = 'yesss'
    should_end_session = False

    if session_attributes["stage"] == 'AccessActivity':
        speech_output = (session_attributes["activity"] + " was your dominant activity. It made you generally " +
                        session_attributes["emotion"] + "! Shall we look at another record? ")
        session_attributes["stage"] = "AnotherTime"

    elif session_attributes["stage"] == 'AnotherTime':
        return AccessRecord(intent, session)

    elif session_attributes["stage"] == 'AddTime':
        speech_output = "Great! What activity made you feel that?"
        session_attributes["stage"] = "AddMood"

    elif session_attributes['stage'] == 'IDK':
        speech_output = "Nice! Do you feel hard to concentrate today?"
        session_attributes['stage'] = "IDK1"
        session_attributes['happy'] = 1

    elif session_attributes['stage'] == 'IDK1':
        speech_output = "A 15 minutes nap probably helps a lot. Were all the decision you made great today?"
        session_attributes['stage'] = "IDK2"

    elif session_attributes['stage'] == 'IDK2':
        speech_output = "Wow! Impressive! Did you have a nice sleep yesterday?"
        session_attributes['stage'] = "IDK3"

    elif session_attributes['stage'] == 'IDK3':
        speech_output = "Good! Do you feel energetic today?"
        session_attributes['stage'] = "IDK4"

    elif session_attributes['stage'] == 'IDK4':
        if session_attributes['happy'] == 1:
            speech_output = "Excellent! Seem like you are spirited today. Is that correct?"
        if session_attributes['happy'] == 0:
            speech_output = "Excellent! Seem like you are a little bit stressed today. Is that correct?"
        session_attributes['stage'] = "IDK5"

    elif session_attributes['stage'] == 'IDK5':
        speech_output = "What makes you feel that?"
        session_attributes['stage'] = "AddMood"

    else:
        speech_output = "Sorry. I don't understand. Please try again or ask what can I say."

    reprompt_text = speech_output
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def Nooo(intent, session):
    session_attributes = session['attributes']
    card_title = 'nooo'
    should_end_session = False

    if session_attributes["stage"] == 'AccessActivity':
        speech_output = (session_attributes["activity"] + " was your dominant activity. It made you generally " +
                        session_attributes["emotion"] + "! Shall we look at another record? ")
        session_attributes["stage"] = "AnotherTime"

    elif session_attributes["stage"] == 'AnotherTime':
        speech_output = "Alright, Rock on!"
        session_attributes["stage"] = "Start"
        return AccessRecord(intent, session)

    elif session_attributes["stage"] == 'AddTime':
        speech_output = "Okay then. Tell me one more time. Try a shorter word."

    elif session_attributes['stage'] == 'IDK':
        speech_output = "Here is a joke for you. How many UC Berkely students does it take to screw a lightbulb? " \
                        "100. 1 to screw the lightbulb, 25 to organize a protest for the lightbulb's right not to light, " \
                        "and 74 to organize a counterprotest. Do you feel hard to concentrate today?"
        session_attributes['stage'] = "IDK1"
        session_attributes['happy'] = 0

    elif session_attributes['stage'] == 'IDK1':
        speech_output = "Wonderful! Keep it that way. Were all the decision you made great today?"
        session_attributes['stage'] = "IDK2"

    elif session_attributes['stage'] == 'IDK2':
        speech_output = "That is okay. You can't always be right. Did you have a nice sleep yesterday?"
        session_attributes['stage'] = "IDK3"

    elif session_attributes['stage'] == 'IDK3':
        speech_output = "Maybe you need to take a warm bath before you sleep. Do you feel energetic today?"
        session_attributes['stage'] = "IDK4"

    elif session_attributes['stage'] == 'IDK4':
        if session_attributes['happy'] == 1:
            speech_output = "Give yourself a short break and it will be fine. Seem like you are calmed today. Is that correct?"
        if session_attributes['happy'] == 0:
            speech_output = "Give yourself a short break and it will be fine. Seem like you are a little bit sad today. Is that correct?"
        session_attributes['stage'] = "IDK5"

    elif session_attributes['stage'] == 'IDK5':
        speech_output = "How are you feeling then?"
        session_attributes['stage'] = "AddTime"
    else:
        speech_output = "Sorry. I don't understand. Please try again or ask 'what can I say'."

    reprompt_text = speech_output
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" + output + "</speak>"
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" + output + "</speak>"
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
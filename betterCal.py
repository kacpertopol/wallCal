#!/usr/bin/env python

import argparse 
import configparser
import os
import datetime
import re
import sys
import datetime

class calConfiguration:
    "Singelton for configuration data." 
    
    # sauce : https://code.activestate.com/recipes/52558/
    
    class __impl:
        def __init__(self):
            script_dir = os.path.dirname(os.path.realpath(__file__))
            path = os.path.join(script_dir , "betterCal.config")
            cparser = configparser.ConfigParser()
            cparser.read(path)    
            self.zone = int(cparser.get("general" , "zone"))
            self.delta = int(cparser.get("general" , "delta"))
            self.yearPattern = re.compile("Y\d\d\d\d")
            self.monthPattern = re.compile("M\d\d")
            self.dayPattern = re.compile("D\d\d")
            self.hourPattern = re.compile("h\d\d")
            self.minutePattern = re.compile("m\d\d")
            self.weekPattern = re.compile("W\d\d")
            self.weekdayPattern = re.compile("w\d")
            self.truePattern = re.compile("true")
            self.andPattern = re.compile("&\)")
            self.orPattern = re.compile("\|\)")
            self.stopPattern = re.compile("\(")
            self.gtDatePattern = re.compile(">\d\d\d\d-\d\d-\d\d") 
            self.ltDatePattern = re.compile("<\d\d\d\d-\d\d-\d\d") 
            self.geDatePattern = re.compile(">=\d\d\d\d-\d\d-\d\d") 
            self.leDatePattern = re.compile("<=\d\d\d\d-\d\d-\d\d") 
            self.gtTimePattern = re.compile(">\d\d:\d\d") 
            self.ltTimePattern = re.compile("<\d\d:\d\d") 
            self.geTimePattern = re.compile(">=\d\d:\d\d") 
            self.leTimePattern = re.compile("<=\d\d:\d\d") 
            self.weekdays = {0 : "MON" , 1 : "TUE" , 2 : "WED" , 3 : "THU" , 4 : "FRI" , 5 : "SAT" , 6 : "SUN"}

    __instance = None

    def __init__(self):
        if calConfiguration.__instance is None:
            calConfiguration.__instance = calConfiguration.__impl()
        self.__dict__['_calConfiguration__instance'] = calConfiguration.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        pass

def getFunction(specification):
    """
    <string> -> ( <date time> -> <boolean>)
    or
    <string> -> ( <date time> -> <NoneType>)

    Takes a time specification and returns a function. 
    This function, when applied to a datetime object
    return either -True- or -False- of the date matches the appropriate
    specification. If none of the specification produce a match the function
    returns -None-.

    Specification examples:

    Y2021         - event in given year
    M03           - event in given month
    D05           - event in given day
    h04           - event in given hour
    m08           - event in given minute
    W05           - event taking place during the fifth week of the year
    w3            - event taking place on a Wednesday
    true          - event taking place constantly
    >2021-03-05   - event after date
    <2021-03-05   - event before date
    >=2021-03-05  - event after or on date
    <=2021-03-05  - event before or on date
    >21:22        - event after time
    <21:22        - event before time
    >=21:22       - event after time or on this time
    <=21:22       - event before time or on this time

    """
    data = calConfiguration()
    if(data.yearPattern.match(specification)):
        return lambda t : int(specification[1:]) == t.year
    elif(data.monthPattern.match(specification)):
        return lambda t : int(specification[1:]) == t.month
    elif(data.dayPattern.match(specification)):
        return lambda t : int(specification[1:]) == t.day
    elif(data.hourPattern.match(specification)):
        return lambda t : int(specification[1:]) == t.hour
    elif(data.minutePattern.match(specification)):
        return lambda t : int(specification[1:]) == t.minute
    elif(data.weekPattern.match(specification)):
        return lambda t : int(specification[1:]) == t.isocalendar().week
    elif(data.weekdayPattern.match(specification)):
        return lambda t : int(specification[1:]) == t.weekday() + 1
    elif(data.truePattern.match(specification)):
        return lambda t : True
    elif(data.gtDatePattern.match(specification)):
        return lambda t : t > datetime.datetime.strptime(specification + " 23:59" , '>%Y-%m-%d %H:%M') 
    elif(data.ltDatePattern.match(specification)):
        return lambda t : t < datetime.datetime.strptime(specification + " 00:00" , '<%Y-%m-%d %H:%M') 
    elif(data.geDatePattern.match(specification)):
        return lambda t : t >= datetime.datetime.strptime(specification + " 00:00", '>=%Y-%m-%d %H:%M') 
    elif(data.leDatePattern.match(specification)):
        return lambda t : t <= datetime.datetime.strptime(specification + " 23:59", '<=%Y-%m-%d %H:%M') 
    elif(data.gtTimePattern.match(specification)):
        def gtTime(t):
            compare = datetime.datetime(
                            year = t.year , 
                            month = t.month , 
                            day = t.day , 
                            hour = int(specification[1:3]),
                            minute = int(specification[4:]))
            return t > compare
        return gtTime
    elif(data.ltTimePattern.match(specification)):
        def ltTime(t):
            compare = datetime.datetime(
                            year = t.year , 
                            month = t.month , 
                            day = t.day , 
                            hour = int(specification[1:3]),
                            minute = int(specification[4:]))
            return t < compare
        return ltTime
    elif(data.geTimePattern.match(specification)):
        def geTime(t):
            compare = datetime.datetime(
                            year = t.year , 
                            month = t.month , 
                            day = t.day , 
                            hour = int(specification[2:4]),
                            minute = int(specification[5:]))
            return t >= compare
        return geTime
    elif(data.leTimePattern.match(specification)):
        def leTime(t):
            compare = datetime.datetime(
                            year = t.year , 
                            month = t.month , 
                            day = t.day , 
                            hour = int(specification[2:4]),
                            minute = int(specification[5:]))
            return t <= compare
        return leTime
    else:
        return specification

def andFunction(lst):
    """
    [ <boolean> ] -> <boolean>

    Applies -and- between boolean values in list.
    """
    val = True
    for v in lst:
        val = v and val
        if(val == False):
            break
    return val

def orFunction(lst):
    """
    [ <boolean> ] -> <boolean>

    Applies -or- between boolean valies in list.
    """
    val = False
    for v in lst:
        val = v or val
        if(val == True):
            break
    return val

def getInEventFunction(string , where = None):
    """
    <string> -> ( <date time> -> <boolean>)

    Given an event specification a function is returned that
    returns -True- if a given date and time falls inside the 
    event. Otherwise -False- is returned. The optional
    argument is a the file and line.

    Additional arguments:

    where - additional information, eg.: file path and line number

    Specification examples:

    Y2021                           - event in given year
    M03                             - event in given month
    D05                             - event in given day
    h04                             - event in given hour
    m08                             - event in given minute
    W05                             - event taking place during the fifth week of the year
    w3                              - event taking place on a Wednesday
    true                            - event taking place constantly
    >2021-03-05                     - event after date
    <2021-03-05                     - event before date
    >=2021-03-05                    - event after or on date
    <=2021-03-05                    - event before or on date
    >21:22                          - event after time
    <21:22                          - event before time
    >=21:22                         - event after time or on this time
    <=21:22                         - event before time or on this time

    Specifications can be joined using ( &) and ( |) that
    take aply the and, or operator to specifications inside.
    Carefull, spaces must be present around the brackets and
    before $,|. Some examples:

    ( ( w3 H14 &) ( w7 H17 &) |)    - event at 14 hours on Wednesday
                                      or 17 hours on Sunday
    ( ( w1 w2 w3 |) H14 &)          - event taking place on 
                                      on Monday or Tuesday or Wednesday
                                      at 14 hours.

    """
    if(string.count("(") != string.count(")")):
        print("-----------------")
        print("Wrong syntax in :")
        print(string)
        if(where):
            print("from :")
            print(str(where))
        print("The number of opening and closing brackets does not match.")
        print("Exiting.")
        print("-----------------")
        sys.exit(1)
    data = calConfiguration()
    specifications = string.split()
    functions = list(map(getFunction , specifications))
    for el in functions:
        if(isinstance(el , str)):
            ok = False
            if(data.andPattern.match(el)):
                ok = True
            if(data.orPattern.match(el)):
                ok = True
            if(data.stopPattern.match(el)):
                ok = True
            if(not ok):
                print("-----------------")
                print("Wrong syntax in :")
                print(string)
                if(where):
                    print("from :")
                    print(str(where))
                print("Unrecognized time specifications in string.")
                print("Exiting.")
                print("-----------------")
                sys.exit(1)
    def result(t):
        stack = [(functions[i] if isinstance(functions[i] , str) else functions[i](t)) for i in range(len(specifications))]
        i = 0
        while(len(stack) > 1):
            if(isinstance(stack[i] , str) and data.andPattern.match(stack[i])):
                j = i - 1
                while(j >= 0):
                    if(isinstance(stack[j] , str) and data.stopPattern.match(stack[j])):
                        break
                    j -= 1
                stack = stack[0 : j] + [andFunction(stack[j + 1 : i])] + stack[i + 1 :]
                if(j < 0):
                    print("-----------------")
                    print("Wrong syntax in :")
                    print(string)
                    if(where):
                        print("from :")
                        print(str(where))
                    print("No closing bracket in string.")
                    print("Exiting.")
                    print("-----------------")
                    sys.exit(1)
                i = j
            elif(isinstance(stack[i] , str) and data.orPattern.match(stack[i])):
                j = i - 1
                while(j >= 0):
                    if(isinstance(stack[j] , str) and data.stopPattern.match(stack[j])):
                        break
                    j -= 1
                stack = stack[0 : j] + [orFunction(stack[j + 1 : i])] + stack[i + 1 :]
                if(j < 0):
                    print("-----------------")
                    print("Wrong syntax in :")
                    print(string)
                    if(where):
                        print("from :")
                        print(str(where))
                    print("No closing bracket in string.")
                    print("Exiting.")
                    print("-----------------")
                    sys.exit(1)
                i = j
            i += 1
        if(len(stack) != 1):
            print("-----------------")
            print("Wrong syntax in :")
            print(string)
            if(where):
                print("from :")
                print(str(where))
            print("Exiting.")
            print("-----------------")
            sys.exit(1)
        return stack[0]
    return result
    
def parseFile(path):
    """
    <string> -> [(<date time> -> <boolean> , <string> , <string>)]

    Given a path to a calendar file, produces a list of events.
    Each event is a tuple. The first element of the tuple
    is a function that when applied to a date time object
    returns -True- if this time is in the event and -False- otherwise.
    The second element of the tuple is the event title. 
    The third element of the tuple is the event body.
    """
    fun = None
    eventTitle = None
    eventBody = None
    inEvent = False
    result = []
    with open(path , "r") as f:
        lnum = 0
        for line in f.readlines():
            lnum += 1
            ls = line.strip()
            if(len(ls) > 2 and ls[0:2] == "# "):
                inEvent = True
                fun = getInEventFunction(ls[1:] , where = " file : " + path + "\n line : " + str(lnum))
            elif(ls == "##"):
                inEvent = False
                if(fun != None and eventTitle != None):
                    if(eventBody == None):
                        result.append((fun , eventTitle , ""))
                    else:
                        result.append((fun , eventTitle , eventBody))
                    fun = None
                    eventTitle = None
                    eventBody = None
            elif(inEvent):
                if(eventTitle == None):
                    eventTitle = ls
                else:
                    if(eventBody == None):
                        eventBody = line
                    else:
                        eventBody += line
    return result

def printDayEvents(path , day , onlyDetails = False , resolution = 30 , alarm = 0 , show_todo = True):
    """
    (<string> , <date time>) -> <stdout output>

    Given a path to a calendar file, a datetime object,
    writes the events to stdout. 

    Additional arguments:

    onlyDetails - if set the events will be printed in text form
    resolution - resolution, in minutes, of the time table
    alarm - if not 0, this is the number of days to search for todo events 
    """
    data = calConfiguration()
    
    events = parseFile(path)
    
    start = datetime.datetime(day.year , day.month , day.day , 0 , 0)
    end = datetime.datetime(day.year , day.month , day.day , 23 , 59)

    deltaL = datetime.timedelta(minutes = resolution)
    delta = datetime.timedelta(minutes = data.delta)

    alarms = set()
    if(alarm != 0):
        for ev in events:
            if((":" in ev[1]) and ("ALARM" == ev[1].split(":")[1].strip())):
                currentDate = start + datetime.timedelta(days = 1)
                while currentDate <= start + datetime.timedelta(days = alarm):
                    if(ev[0](currentDate)):
                        tle = ev[1].split(":")[0].strip()
                        alarms.add(tle)
                    currentDate += delta
            
    if(onlyDetails):
        todos = []
        sys.stdout.write("# EVENTS ON " + str(start.year) + "-" + str(start.month).zfill(2) + "-" + str(start.day).zfill(2) + "\n")
        for ev in events:
            if((":" in ev[1]) and ("TODO" == ev[1].split(":")[1].strip())):
                tle = ev[1].split(":")[0].strip()
                todos.append(tle)
            else:
                tms = ""
                prvIn = False
                curIn = None
                currentDate = start
                while currentDate <= end:
                    if(ev[0](currentDate)):
                        curIn = True
                    else:
                        curIn = False
                    if((not prvIn) and curIn):
                        tms += str(currentDate.hour).zfill(2) + ":" + str(currentDate.minute).zfill(2) + "-"
                    if(prvIn and (not curIn)):
                        tms += str(currentDate.hour).zfill(2) + ":" + str(currentDate.minute).zfill(2) + ""
                    prvIn = curIn
                    currentDate += delta
                if(tms != ""): 
                    #print(ev , tms)
                    sys.stdout.write("\n")
                    tle = ev[1]
                    if(":" in tle):
                        tle = tle.split(":")[0].strip()
                    sys.stdout.write("## " + tle + " , ")
                    sys.stdout.write(tms)
                    if(ev[2] != ""):
                        sys.stdout.write("\n\n" + ev[2])
                    else:
                        sys.stdout.write("\n")
        if(alarm != 0):
            sys.stdout.write("\n")
            sys.stdout.write("# IMPORTANT EVENTS FROM THE FOLLOWING " + str(alarm) + " DAYS :\n")
            sys.stdout.write("\n")
            for e in alarms:
                sys.stdout.write("- " + e + "\n")
        if(show_todo):
            sys.stdout.write("\n")
            sys.stdout.write("# THINGS TO DO :\n")
            sys.stdout.write("\n")
            for e in todos:
                sys.stdout.write("- " + e + "\n")
            sys.stdout.write("\n")
    else:
        sys.stdout.write("\nEVENTS ON " + str(data.weekdays[start.weekday()]) + " , " + str(start.year) + "-" + str(start.month).zfill(2) + "-" + str(start.day).zfill(2) + " :\n")
        sys.stdout.write("\n")
        currentDateL = start
        while currentDateL <= end:
            if (currentDateL - deltaL).minute == 0:
                #sys.stdout.write(u'\u2595')
                sys.stdout.write(u'\u258f')
            elif currentDateL.minute == 0:
                hour = str(currentDateL.hour)
                if(len(hour) == 1):
                    sys.stdout.write("0")
                else:
                    sys.stdout.write(hour[0])
            else:
                sys.stdout.write(" ")
            currentDateL += deltaL
        sys.stdout.write("\n")

        currentDateL = start
        while currentDateL <= end:
            if (currentDateL - deltaL).minute == 0:
                #sys.stdout.write(u'\u2595')
                sys.stdout.write(u'\u258f')
            elif currentDateL.minute == 0:
                hour = str(currentDateL.hour)
                if(len(hour) == 1):
                    sys.stdout.write(hour[0])
                else:
                    sys.stdout.write(hour[1])
            else:
                sys.stdout.write(" ")
            currentDateL += deltaL
        sys.stdout.write("\n")

        todos = []
        for ev in events:
            if((":" in ev[1]) and ("TODO" == ev[1].split(":")[1].strip())):
                tle = ev[1].split(":")[0].strip()
                todos.append(tle)
            else:
                #sys.stdout.write(" ")
                lne = " "
                notEmptyDay = False
                currentDateL = start
                while currentDateL < end:
                    isIn = False
                    currentDate = currentDateL
                    while currentDate < currentDateL + deltaL:
                        if(ev[0](currentDate)):
                            isIn = True
                        currentDate += delta
                    if(isIn):
                        #sys.stdout.write(u'\u2588')
                        notEmptyDay = True
                        lne += u'\u2588'
                    else:
                        #sys.stdout.write(u'\u258f')
                        lne += u'\u258f'
                    currentDateL += deltaL
                tle = ev[1]
                if(":" in tle):
                    tle = tle.split(":")[0].strip()
                #sys.stdout.write(u'\u258f' + tle)
                lne += u'\u258f' + tle
                #sys.stdout.write("\n")
                lne += "\n"
                if(notEmptyDay):
                    sys.stdout.write(lne)
        if(alarm != 0):
            sys.stdout.write("\n")
            sys.stdout.write("IMPORTANT EVENTS FROM THE FOLLOWING " + str(alarm) + " DAYS :\n")
            sys.stdout.write("\n")
            for e in alarms:
                sys.stdout.write(e + "\n")
        if(show_todo):
            sys.stdout.write("\n")
            sys.stdout.write("THINGS TO DO :\n")
            sys.stdout.write("\n")
            for e in todos:
                sys.stdout.write(e + "\n")


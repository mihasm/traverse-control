"""
Author: Miha Smrekar
Date: December, 2018

===== ISEL IMC-S8 DNC MODE SOFTWARE IMPLEMENTATION =====

1. Description

    This is a high-level implementation of the serial protocol used by
    Dantec Translate Mechanism used for measuring Wind speed with laser measurmenet system.

    The controller used to control the translator is the ISEL IMC-S8.
    https://www.isel.com/en/mwdownloads/download/link/id/4248/

    The IMC-S8 integrates four motor power amplifiers with step/direction interface.
    The mode used to connect the controler to a PC via serial interface is called DNC-mode.
    The controller is then able to drive stepper motors using full steps or micro steps (128 / full step).

    The interface to the controller is realized using RS232.
    Pins 2 and 3 are used for RxD and TxD. Pin 5 is used for ground reference.
    The communication protocol realizes the faultless transmission of ASCII characters.

    The control PC (PC) sends a command that ends with a line end character [CR, char(13)].
    The processor units quits the execution with the quitting signal 0 [char(48)],
        or returns an occured error with an ASCII character unequal 0.

2. Data transfer parameters:
    -19200 baud
    -8 data bits
    -1 stop bit
    -no parity

3. Maximum values:
    -maximum x value is 327975 +- 1000
    -maximum y value is 328170 +- 1000
    -maximum z value is 328120 +- 1000
    -Supposedly 320 ticks equals 1 mm. So the maximum range is 1m x 1m x 1m.
    NOTE:   If maximum value is reached, the controller stops because of an end switch with error 2.
            For any further movement to be executed, reference_run() needs to be executed

4. Reference values:
    slow speed = 1000
    normal speed = 5000
    fast speed = 10000

5. Usage instructions:
    a) Install Python 3.x.x.
        a.1) Check that python is working
        a.2) Check that pip is working
    b) Install necessary requirements (serial module) by moving into the software folder and running "pip install -r requirements.txt".
    c) Plug in the USB cable (RS232) into the computer and into the controller.
    d) Find the right port of the usb cable ("COM1-9" on Windows - Device Manager / "etcx" on Linux).
    e) Change the port in this script by editing the initialization portion of the serial module.
    f) Using bash/cmd, move into the software folder, that contains this script,
        and start the python interpreter by typing >>python and pressing Enter.
    g) Import the functions from this script and the serial object into the interpreter (RAM),
        using the command "import commands"
    h) Now you can run the functions in the script
    i) This is an example of the optimum execution sequence, with example code:
        i.1) initialize()
        i.2) get_version_data()
        i.3) reference_run()
        i.4) get_position()
        i.5) execute_absolute_movement(500,500,500,plane="zy") #in millimeters from the origin
        i.6) traverse_plane(_min=0,_max=500,step=100,delay=5,plane="zy") #for traversing a plane
"""

import serial
import time


#This is the initialization portion of the serial module.

ser = serial.Serial(
    port='COM9',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1)


def initialize(num_axes=3,controller=0):
    """
    Initializes the controller and sets the number of axes.

    num_axes is an int between 1 and 3
    1 ... x
    2 ... x,y
    3 ... x,y,z
    controller is 0 by default
    """
    num_axes = int(num_axes)
    if num_axes == 1:
        s = "@%s1" % str(controller)
        return transmit_command(s.encode("ascii"),False)
    elif num_axes == 2:
        s = "@%s3" % str(controller)
        return transmit_command(s.encode("ascii"),False)
    elif num_axes == 3:
        s = "@%s7" % str(controller)
        return transmit_command(s.encode("ascii"),False)
    else:
        raise Exception("Not able to initialize %s axes" % str(num_axes))

def get_version_data(controller=0):
    """
    Fetches controller version data.
    """
    s = "@%sV\r" % controller
    s = s.encode("ascii")
    return transmit_command(s)

def reference_run(controller=0,axes=7):
    """
    Used after axes initialization to return the traverse system to its origin (0,0,0).
    """
    s = "@%sR%s\r" % (controller,axes)
    s = s.encode("ascii")
    return transmit_command(s)

def transmit_command(raw_command,wait=True):
    """
    Transmits the raw command to the controller.
    Returns the controller's raw response.
    If wait is True, then waits for return character from the controller.
    If wait is False, then we assume that the command transmitted
                does not require a response from the controller.
    """

    
    print("TX",raw_command)

    #Sending the command
    ser.write(raw_command)

    #Reading the response
    raw_response = ser.read_until("\r")

    #Used to wait for the response
    if wait == True:
        #Read the responses until length of a response is greater than zero.
        while len(raw_response) == 0:
            raw_response = ser.read_until("\r")

    print("RX",raw_response)
    return raw_response

def error_check_response(response):
    """
    This function helps determining error response codes from the controller.
    """
    response_str = str(response)

    #tuple[0] provides error description
    #tuple[1] is True, if error was so severe that initialising (reference run) is needed again
    error_descriptions = {
    "0":["No error, the command was executed correctly",False],
    "1":["Error in numeric value provided",False],
    "2":["End switch error",True],
    "3":["Incorrect axis specification",False],
    "4":["No axis defined",False],
    "5":["Syntax error",False],
    "6":["End of memory",False],
    "7":["Incorrect number of parameters",False],
    "8":["Command to be stored is incorrect",False],
    "9":["System error",True],
    "D":["Speed not permitted",False],
    "F":["User stop",False],
    "G":["Invalid data field",False],
    "H":["Cover error",False],
    "R":["Reference error",False],
    "=":["Not used by this controller",False]
    }

    if response_str in error_descriptions:
        print (error_descriptions[response_str][0])
        if response_str == "0":
            return "0"
        else:
            return error_descriptions[response_str][1]
    else:
        raise Exception("Execution stopped because controller response was not expected: %s" % response_str)

def _get_position(controller=0):
    """
    Gets raw position information.
    """
    s = "@%sP\r" % controller
    s = s.encode("ascii")
    return transmit_command(s)

def get_position(controller=0):
    """
    Gets position in millimeters from origin for each axis.
    """
    res = _get_position(controller)
    status,x,y,z=res[0],res[1:7],res[7:13],res[13:]
    x = int(x,16)
    y = int(y,16)
    z = int(z,16)
    print("x:",x/320.,"y:",y/320.,"z:",z/320.)

def execute_absolute_movement(
    pos_x,
    pos_y,
    pos_z,
    speed_xyz=(10000,10000,10000),
    pos_z2=0,speed_z2=20,
    controller=0,axes=3):

    """
    Executes an absolute movement.
    Default speed for all axes is 10000.
    Maximum value of position is 1000 for each axis.
    """
    print("Executing absolute movement")

    #Check bounds
    if pos_x > 1000 or pos_x < 0 or pos_y > 1000 or pos_y < 0 or pos_z > 1000 or pos_z < 0:
        raise Exception("XYZ coordinates have to be in range 0,1000 [in mm]")

    #Create string
    s = "@%sM%s,%s,%s,%s,%s,%s,%s,%s\r" % (controller,
        int(pos_x*320),speed_xyz[0],
        int(pos_y*320),speed_xyz[1],
        int(pos_z*320),speed_xyz[2],
        pos_z2,speed_z2
        )
    s = s.encode("ascii")
    return transmit_command(s)

def generate_coordinate_plane(_min,_max,step,plane="zy"):
    """
    Generates list of coordinates in a single plane.

    _min determines the minimum value
    _max determines the maximum value
    step determines the step size

    Example:
    >generate_coordinate_plane(1,3,1,plane="xy") should return 9 elements:
    > [(1, 1, 0), (1, 2, 0), (1, 3, 0), (2, 3, 0), (2, 2, 0), (2, 1, 0), (3, 1, 0), (3, 2, 0), (3, 3, 0)]
    >generate_coordinate_plane(1,3,1,plane="yx") should return 9 elements:
    > [(1, 1, 0), (2, 1, 0), (3, 1, 0), (3, 2, 0), (2, 2, 0), (1, 2, 0), (1, 3, 0), (2, 3, 0), (3, 3, 0)]
    """
    coordinate_map_to_int = {"x":0,"y":1,"z":2}
    lst = []
    cur_a,cur_b = _min,_min
    positive_traversal = True
    while cur_a <= _max:
        if positive_traversal:
            while cur_b <= _max:
                lst.append((cur_a,cur_b))
                cur_b += step
            cur_b -= step
            positive_traversal = False
        else:
            while cur_b >= _min:  
                lst.append((cur_a,cur_b))
                cur_b -= step
            cur_b += step
            positive_traversal = True
        cur_a += step

    lst_xyz = []
    if plane == "yz":
        for a,b in lst:
            lst_xyz.append((0,a,b))
    elif plane == "zy":
        for a,b in lst:
            lst_xyz.append((0,b,a))
    elif plane == "xy":
        for a,b in lst:
            lst_xyz.append((a,b,0))
    elif plane == "yx":
        for a,b in lst:
            lst_xyz.append((b,a,0))
    elif plane == "xz":
        for a,b in lst:
            lst_xyz.append((a,0,b))
    elif plane == "zx":
        for a,b in lst:
            lst_xyz.append((b,0,a))
    else:
        raise Exception("Plane %s is not a valid Cartesian Coordinate plane, options are: xy,yx,zx,xz,yz,zy" % plane)

    return lst_xyz

def traverse_plane(_min,_max,step,delay=5,plane="zy"):
    """
    Moves the traverse system along a plane using the shortest path.

    Plane can be xy,yx,xz,zx,yz,zy.

    _min determines the first coordinate pair (based on plane)
    _maxdetermines the last coordinate pair (based on plane)
    step determines the step size
    delay means the time that the traverse system is stopped in a single point in space.
    """
    lst_xyz = generate_coordinate_plane(_min,_max,step,plane)
    #print(lst_xyz)
    print("Measuring plane made of %s points..." % str(len(lst_xyz)))
    print("List of points:",lst_xyz)
    for x,y,z in lst_xyz:
        print("Moving to x:%s,y:%s,z:%s ..." % (x,y,z))
        execute_absolute_movement(x,y,z)
        print("Position x:%s,y:%s,z:%s reached!" % (x,y,z))
        print("Waiting %s seconds..." % delay)
        time.sleep(delay)

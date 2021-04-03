#!/usr/bin/env python3
'''
 Copyright (c) 2012 Sekou Remy
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
'''

import roslib
roslib.load_manifest('geometry_msgs')
import rospy
import web
from math import sin,cos
from geometry_msgs.msg import Pose

class pose_converter:
        def __init__(self):
                rospy.init_node('pose_converter', anonymous=True)
                self.num_robots=int(rospy.get_param('~num_robots',1))
                self.publishers = [None]*self.num_robots; 
                self.subscribers = [None]*self.num_robots; 
                if rospy.has_param('~robot_prefix'): #if there is a robot prefix assume that there is actually one or more
                    #full_param_name = rospy.search_param('robot_prefix')
                    #robot_prefix = rospy.get_param(full_param_name)
                    robot_prefix=rospy.get_param('~robot_prefix')
                    for r in range(self.num_robots):
                       self.publishers[r]=rospy.Publisher(robot_prefix+str(r)+'/pose',Pose,queue_size=10);
                else: # if no robot prefix, assume that there is only one robot
                    self.publishers[0] = rospy.Publisher('pose',Pose,queue_size=10);rospy.logwarn("assuming /pose, number of robots actually"+str(self.num_robots))

                self.data_uri = rospy.get_param("data_uri","/pose");
                self.urls = (self.data_uri,'pose', "/stop","stop")
                self.data = ['-10']*self.num_robots;
                self.port=int(rospy.get_param("~port","8080"));
                rospy.logwarn("running")
class stop:
        def GET(self):
                return exit(0)
        def POST(self):
                return exit(0)
class pose:
        def GET(self):
                return self.process()
        def POST(self):
                return self.process()
        def process(self):
                global pc
                msg=Pose();
                robot_id=0;
                i = web.input();
                try:
                        if hasattr(i, "px"):
                                msg.position.x = float(i.px)
                        if hasattr(i, "py"):
                                msg.position.y = float(i.py)
                        if hasattr(i, "pz"):
                                msg.position.z = float(i.pz)
                        if hasattr(i, "ox"):
                                msg.orientation.x = float(i.ox)
                        if hasattr(i, "oy"):
                                msg.orientation.y = float(i.oy)
                        if hasattr(i, "oz"):
                                msg.orientation.z = float(i.oz)
                        if hasattr(i, "ow"):
                                msg.orientation.w = float(i.ow)
                        if hasattr(i, "a"):
                                a=float(i.a)
                                (msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w) = (0,0,sin(a/2),cos(a/2))
                        if hasattr(i, "id"):
                                robot_id = int(i.id)
                        if robot_id < pc.num_robots: pc.publishers[robot_id].publish(msg);
                except Exception as err:
                        rospy.logwarn("Cannot convert/publish due to %s" % err)

                data = '';
                size = 0
                web.header("Content-Length", str(size)) # Set the Header
                #output to browser
                web.header("Content-Type", "text/plain") # Set the Header
                return data

pc = pose_converter()
app = web.application(pc.urls, globals())

if __name__ == "__main__":
        wsgifunc = app.wsgifunc()
        wsgifunc = web.httpserver.StaticMiddleware(wsgifunc)
        server = web.httpserver.WSGIServer(("0.0.0.0",  pc.port),wsgifunc)
        print("http://%s:%d/%s" % ("0.0.0.0", pc.port, pc.urls))
        try:
                server.start()
        except (KeyboardInterrupt, SystemExit):
                server.stop()
                print("Shutting down service")

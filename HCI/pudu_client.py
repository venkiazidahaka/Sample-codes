import requests
import json


class PUDUROBOT():

    _defaults = {
        "File_start_path": 'C:/Users/staff/Desktop/案件/PUDUTECH/SDK/SDK/PuduRobotOpenServer-win.exe',
        "check_header": "http://127.0.0.1:9050/api/devices",
        "robot_group_header": "http://127.0.0.1:9050/api/robot/groups?device=",
        "robot_header1": "http://127.0.0.1:9050/api/robots?device=",
        "robot_header2": "&group_id=",
        "destination_header1": "http://127.0.0.1:9050/api/destinations?device=",
        "destination_header2": "&robot_id=",
        "destination_header3": "&page_size=300&page_index=",
        "group_status_header1": "http://127.0.0.1:9050/api/robot/state?device_id=",
        "group_status_header2": "&group_id=",
        "group_status_header3": "&timeout=5&count=5",
        "robot_status_header1": "http://127.0.0.1:9050/api/robot/status?device_id=",
        "robot_status_header2": "&robot_id=",
        "call_robot_header": "http://127.0.0.1:9050/api/robot/call",
        "cancel_call_robot_header": "http://127.0.0.1:9050/api/robot/cancel/call",
        "delivery_robot_header": "http://127.0.0.1:9050/api/robot/delivery/task",
        "robot_action_header": "http://127.0.0.1:9050/api/robot/action",
        "robot_get_map_header1": "http://127.0.0.1:9050/api/robot/map?device_id=",
        "robot_get_map_header2": "&robot_id=",
        "notification_server_header": "http://127.0.0.1:9050/api/notify/url"
    }

    def __init__(self, **kwargs):
        """
        Use this Class to control PUDU Robots and access the PUDU SDK SERVER.\n
        NOTE: Make sure that the SDK NODE SERVER is always running in the background to avoid connection errors. """
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)

######################################### Check if the API Key is added to the PUDU Server ############################################

        header = self.__dict__["check_header"]
        # Send the GET request to the server and check the response data
        response = requests.get(header)

################################################## Add the device to the PUDU Server ##################################################

        try:
            self.header = self.__dict__["header"]
            # SDK data recieved from the Pudu IOT Platform
            self.body = self.__dict__["body"]
            # Post the request to the Server to add the device
            response = requests.post(self.header, json=self.body)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

######################################### Get the Robot Group DATA from the PUDU Server ################################################

        robot_group_header = self.__dict__[
            "robot_group_header"]+self.device_id
        # Send the GET request to the server to recieve the Robot Group data
        response = requests.get(robot_group_header)
        # get the data in JSON format
        robot_group_data = json.loads(response.text)
        # Make a list of all the robots with their robot id
        robotgroup_id = robot_group_data["data"]["robotGroups"]
        robotgroup_id_list = []
        for robotgroup_id_dic in robotgroup_id:
            temp = robotgroup_id_dic["id"]
            robotgroup_id_list.append(temp)
        self.robotgroup_id_list = robotgroup_id_list

###################### Create a dictionary with the Shop name, Robot name and the Robot IDs in the group ###############################

        robot_id_dic = {}
        for robotgroup_id_indiv in robotgroup_id_list:
            temp_dict = {}
            gid_dict = {}

############################################ Get the Robot IDs in the Robot Group ######################################################

            robot_header = self.__dict__[
                "robot_header1"]+self.device_id+self.__dict__["robot_header2"] + robotgroup_id_indiv

####################### Send a GET request to the PUDU Server to recieve the Robot ID's from the Robot Group ###########################

            response = requests.get(robot_header)
            robot_data = json.loads(response.text)
            robot_id = robot_data["data"]["robots"]
            for dictionary in robot_id:
                temp_dic = {dictionary["name"]: dictionary["id"]}
                temp_dict.update(temp_dic)
            gid_dict[robotgroup_id_indiv] = temp_dict
            if len(robot_id_dic) == 0:
                robot_id_dic[self.store_name] = gid_dict
            else:
                robot_id_dic[self.store_name].update(gid_dict)
        self.robot_id_dict = robot_id_dic
        # print(self.robot_id_dict)
        for group_id in self.robot_id_dict[self.store_name].keys():
            if self.robot_name in robot_id_dic[self.store_name][group_id].keys():
                self.robot_group_id = group_id
                # print(self.robot_group_id)

    def add_notification_server(self, url_link):
        notification_server_header = self.__dict__[
            "notification_server_header"]
        body = {"url": url_link}
        response = requests.post(notification_server_header, json=body)

    def get_destinations(self):
        """
        Get the destinations of the particular robot from the maps. \n
        NOTE: This function creates a custom dictionary of the json data recieved from the PUDU SERVER

        Returns:
            [DICTIONARY]: Returns a custom dictionary of all the points in the current map of the robot
        """

        # create a custom dictionary of destination types and destination names
        destination_dic = {}
        i = 1
        while True:
            try:
                dest_header = self.__dict__[
                    "destination_header1"]+self.device_id+self.__dict__[
                    "destination_header2"]+self.robot_id_dict[self.store_name][self.robot_group_id][self.robot_name]+self.__dict__["destination_header3"]+str(i)
                i = i+1
                response = requests.get(dest_header)
                destination_json = json.loads(response.text)
                destination_data = destination_json["data"]["destinations"]

                if len(destination_data) != 0:
                    for dictionary in destination_data:

                        temp_dic = {dictionary["type"]: [dictionary["name"]]}
                        if dictionary["type"] not in destination_dic:
                            destination_dic.update(temp_dic)

                        elif len(destination_dic[dictionary["type"]]) >= 1:
                            destination_dic[dictionary["type"]
                                            ].append(dictionary["name"])
                else:
                    break
            except Exception as error:
                print(error)
                break
        return destination_dic

    def get_robot_group_status(self):
        """
        Get the status of all the robots in the particular group. \n
        NOTE: The robot group name and the robot group id is required to get the status of the particular robot

        Args:
            group_id(str, optional): The key in the Robot ID Dictionary to get the group id of the robot . Defaults to 'gid'.

        Returns:
            [DICTIONARY]: The robot group status of the particular store
        """
        try:
            robot_group_status_header = self.__dict__[
                "group_status_header1"]+self.device_id+self.__dict__["group_status_header2"]+self.robot_group_id + self.__dict__["group_status_header3"]
            response = requests.get(robot_group_status_header)
            group_status = json.loads(response.text)
            return group_status
        except Exception as error:
            print(error)

    def get_robot_status(self):
        """Get the status of the particular robot in the robot group.

        Returns:
            [STRING]: Returns the move status, robot state and the power of the robot
        """
        robot_status_header = self.__dict__[
            "robot_status_header1"]+self.device_id+self.__dict__["robot_status_header2"]+self.robot_id_dict[self.store_name][self.robot_group_id][self.robot_name]
        try:
            response = requests.get(robot_status_header)
            robot_status_dict = json.loads(response.text)
            robot_move_status = robot_status_dict["data"]["moveState"]
            robot_state = robot_status_dict["data"]["robotState"]
            robot_power = robot_status_dict["data"]["robotPower"]
            robot_pose_dict = robot_status_dict["data"]["robotPose"]
            return robot_move_status, robot_state, robot_power, robot_pose_dict
        except Exception as error:
            print(error)
            return None, None, None, None

    def call_robot(self, destination_dic, dest_name="1"):
        """Call the particular robot from the group to a particular destination point. \n
        NOTE: The function is used only to call the robot to a particular place so the robot does not return back to the HOME position

        Args:
            destination_dic (dictionary): List of all the destinations of the current map
            dest_name (str, optional): The name of the destination where the robot is to be sent. Defaults to "1".

        Returns:
            [BOOL]: If the call is successful,then the robot returns True as the status code
        """

        call_robot_header = self.__dict__["call_robot_header"]
        for robot_dest_type in destination_dic.keys():
            if dest_name in destination_dic[robot_dest_type]:
                dest_type = robot_dest_type
        call_robot_body = {
            "deviceId": self.device_id,
            "robotId": self.robot_id_dict[self.store_name][self.robot_group_id][self.robot_name],
            "destination": {
                "name": dest_name,
                "type": dest_type
            }
        }
        try:
            requests.post(call_robot_header, json=call_robot_body)
        except Exception as error:
            print("Robot call Error! ")
            print(error)

    def cancel_call_robot(self, destination_dic, dest_name="1"):
        """Call this function to cancel the robot tasks

        Args:
            destination_dic (dictionary): List of all the destinations of the current map
            dest_name (str, optional): The name of the destination where the robot is to be sent. Defaults to "1".
        """

        cancel_call_robot_header = self.__dict__["cancel_call_robot_header"]
        for robot_dest_type in destination_dic.keys():
            if dest_name in destination_dic[robot_dest_type]:
                dest_type = robot_dest_type
        cancel_call_robot_body = {
            "robotId": self.robot_id_dict[self.store_name][self.robot_group_id][self.robot_name],
            "deviceId": self.device_id,
            "destination": {
                "name": dest_name,
                "type": dest_type
            }
        }
        try:
            requests.post(
                cancel_call_robot_header, json=cancel_call_robot_body)
        except Exception as error:
            print("Robot call cancel Error! ")
            print(error)

    def robot_delivery(self, dest_name_list, delivery_type="new", delivery_sort="auto", execute_task="true"):
        """Call this function to send a delivery task to the robot

        Args:
            dest_name_list (LIST): Set of all the destinations per tray
            delivery_type (str, optional): Type of delivery. Defaults to "new".
            delivery_sort (str, optional): Configure to send the robot chronologically. Defaults to "auto".
            execute_task (str, optional): Configure whether to begin the task. Defaults to "true".
        """
        tray_list = []
        for i, dest in enumerate(dest_name_list):
            destin_dict = {}
            destin_list = []
            mast_dict = {}
            destin_dict["destination"] = dest
            destin_dict["id"] = str(i)
            destin_list.append(destin_dict)
            mast_dict["destinations"] = destin_list
            tray_list.append(mast_dict)

        delivery_robot_header = self.__dict__["delivery_robot_header"]
        delivery_robot_body = {
            "deviceId": self.device_id,
            "robotId": self.robot_id_dict[self.store_name][self.robot_group_id][self.robot_name],
            "type": delivery_type,
            "deliverySort": delivery_sort,
            "executeTask": execute_task,
            "trays": tray_list
        }
        try:
            requests.post(
                delivery_robot_header, json=delivery_robot_body)
        except Exception as error:
            print("Robot delivery Error! ")
            print(error)

    def exec_task(self, robot_action="Start"):
        """Use this function as a send button which replicates the function of GO button in the robot delivery interface

        Args:
            robot_action (str, optional): Configure to start the current robot task. Defaults to "Start".
        """
        robot_action_header = self.__dict__["robot_action_header"]
        robot_action_body = {
            "robotId": self.robot_id_dict[self.store_name][self.robot_group_id][self.robot_name],
            "deviceId": self.device_id,
            "action": robot_action
        }
        try:
            requests.post(robot_action_header, json=robot_action_body)
        except Exception as error:
            print(error)

    def get_map(self):
        """Call this function to get the current map of the robot
        """
        robot_get_map_header = self.__dict__[
            "robot_get_map_header1"]+self.device_id+self.__dict__["robot_get_map_header2"] + self.robot_id_dict[self.store_name][self.robot_group_id][self.robot_name]
        response = requests.get(robot_get_map_header)
        print(response.text)

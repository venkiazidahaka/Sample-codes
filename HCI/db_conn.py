import pymongo


class MONGODB():
    """Establish connection and work with the MONGO database.

    Returns:
        _type_: _description_
    """
    _defaults = {
        "database_name": "",
        "conn_topo": "",
        "conn_head": ""
    }

    def __init__(self, **kwargs):
        """ Initialize the database connection.

        NOTE: Input the username and password to allow access to the database. Make sure the usernames are provided necessary access to the database to avoid access errors.
        """
        self.username = input("Enter the username to access the database: ")
        self.password = input("Enter the password: ")
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)
        connection = self.__dict__["conn_topo"]+self.username + \
            ":"+self.password + \
            self.__dict__["conn_head"]+self.__dict__["database_name"]
        self.client = pymongo.MongoClient(connection)
        self.sensor_list = []

    def get_collection(self, collection_name):
        """ Get the specified collection data from the database

        Args:
            collection_name (str): Enter the collection name which has to be accessed from the Mongo database
        """
        self.db = self.client[self.__dict__["database_name"]]
        self.collection = self.db[collection_name]

    def get_database_data(self, limit=None):
        """ Iterates through all the documents from the specific collection within the specified limit and retrieves the data.

        Args:
            limit (int): Enter the data retrieve limit

        Returns:
            list: List contains multiple documents in json format within the specified limit
        """
        database_list = []
        items = self.collection.find()
        if not limit:
            for item in items[:limit]:
                database_list.append(item)
        else:
            for item in items:
                database_list.append(item)
        return database_list


if __name__ == "__main__":
    conn = MONGODB()
    conn.get_collection("sensor_data")
    database_list = conn.get_database_data()
    print(len(database_list))
    for item in database_list:
        sensor = item["sensor"]
        if sensor not in conn.sensor_list:
            conn.sensor_list.append(sensor)
    print(conn.sensor_list)

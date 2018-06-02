import sqlite3

SELECT_QUERY_BASE = "SELECT * FROM %s"
SELECT_MOBILE_TOKEN_BY_CLIENT_ID = SELECT_QUERY_BASE + " WHERE client_id='%s'"
SELECT_CLIENT_ID_BY_AP_UUID = SELECT_QUERY_BASE + " WHERE ap_uuid='%s'"
SELECT_AP_IP_PORT_BY_AP_UUID = SELECT_QUERY_BASE + " WHERE ap_uuid='%s'"

class DBWrapper:
    def __init__(self, dbPath="./client.db"):
        self._con = sqlite3.connect(dbPath, check_same_thread=False)
        self._cursor = self._con.cursor()

    def select_mobile_token_by_ap_uuid(self, uuid):
        query = SELECT_CLIENT_ID_BY_AP_UUID % ("ap_info", uuid)
        self._cursor.execute(query)
        ap_infos = self._cursor.fetchall()

        mobile_tokens = list()
        for ap_info in ap_infos:
            query = SELECT_MOBILE_TOKEN_BY_CLIENT_ID % ("client_info", ap_info[0])
            self._cursor.execute(query)
            client_infos = self._cursor.fetchall()

            for client_info in client_infos:
                mobile_tokens.append(client_info[1])

        return mobile_tokens


    def select_ap_ip_port_by_ap_uuid(self, uuid):
        query = SELECT_AP_IP_PORT_BY_AP_UUID % ("ap_info", uuid)
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        for row in rows:
            return row[2], row[3]

    def __del__(self):
        self._cursor.close()
        self._con.close()
from pyfcm import FCMNotification
from ServerApp.DBWrapper import DBWrapper
import socket
import pickle
import hashlib
import elasticsearch
from elasticsearch import Elasticsearch, helpers
import os

#todo : static strings export to seperate file

# API KEY
FCM_API_KEY = "AAAAqpUjsQA:APA91bHjT1sqmCJzoIc6ZO3D0QO9kcsltMnUaz8ZYEN9lSNvUAkX69ApmyOYU3sPWoYf0P3pvK5v30I29jFlCq6A1hLdJjC7hrEZHZq1_3ofUcc4cJYnR7k93v7CdU865isOi2N7H8Ru"
# FCM DEVICE TOKEN
FCM_DEVICE_id = "fwX34j_n-xU:APA91bH_eva4gcXBoebGME1dU-woKxEZYKSwWPOMfYnjo2_cw-vxrYjii92MkjVh90QYc9zbJayr1nGZahqFUc1Kq44Q6v7tA4Fhd7vbhKrPnzaUIIPtu8agNkOJVUpiG-MEMm9Jw820"

# Messages
ALERT_TITLE = "보안 위협 알림"
ALERT_MESSAGE = "가입하신 IoT 서비스가 보안 위협에 노출되었습니다. IoT 서비스사에 문의바랍니다."

# White Files Path
WHITE_FILE_PATH = "./white_files"

# Elasticsearch Server Info
ES_IP = "39.118.41.18"
ES_PORT = "49200"

class ResponseToSecurityIssue:
    def __init__(self, alert_data):
        self.db = DBWrapper()
        self.alert_data = alert_data
        self.push_alarm_to_client()
        self.operate_collect_bin()

    def push_alarm_to_client(self) :

        #Setup API KEY
        push_service = FCMNotification(api_key=FCM_API_KEY)

        if "ap_uuid" in self.alert_data:
            tokens = self.db.select_mobile_token_by_ap_uuid(self.alert_data["ap_uuid"])

            for token in tokens:
                result = push_service.notify_single_device(registration_id=token, message_title=ALERT_TITLE, message_body=ALERT_MESSAGE)
                if result is True:
                    print() # add logger to success
                else:
                    print() # add logger to fail

    def operate_collect_bin(self):

        def check_elf_file(file_path):
            fd = open(file_path, "rb")
            signature = fd.read(4)
            if signature == b"\x7fELF":
                return True
            else:
                return False

        def get_white_hash_list(path):
            white_hash_list = list()

            for path, dir, files in os.walk(path):
                for file in files:
                    file_path = "%s/%s" % (path, file)
                    try:
                        if check_elf_file(file_path) == False: continue
                        fd = open(file_path, "rb")
                    except Exception as e:
                        continue
                    else:
                        hash_md5 = hashlib.md5()
                        for chunk in iter(lambda: fd.read(4096), b""):
                            hash_md5.update(chunk)

                        white_hash_list.append((file_path, hash_md5.hexdigest()))
            return white_hash_list

        OPERATE_COLLECT_BIN = {
            "operator": "get_black_bin",
            "white_hash_list": get_white_hash_list(WHITE_FILE_PATH)
        }

        if "ap_uuid" in self.alert_data:
            ip, port = self.db.select_ap_ip_port_by_ap_uuid(self.alert_data["ap_uuid"])
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, int(port)))
                data = pickle.dumps(OPERATE_COLLECT_BIN)
                s.sendall(data)

class ElasticsearchWrapper:
    def __init__(self, newFile):
        self.file = newFile
        self.es = Elasticsearch([ES_IP], port=ES_PORT, timeout=30)

    def get_file_hash(self):
        hash_md5 = hashlib.md5()
        fd = open(str(self.file.file), "rb")

        for chunk in iter(lambda : fd.read(4096), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def insert_to_elasticsearch(self):
        hash_md5 = self.get_file_hash()
        file_name = str(self.file.file)

        data = [{
            "_index": "black_file_list",
            "_type": "file_info",
            "_source": {
                "file_hash": hash_md5,
                "file_path": file_name
            }
        }]

        result = elasticsearch.helpers.bulk(self.es, data)

        # add logger by result
from dyn.tm.session import DynectSession
from dyn.tm.zones import Zone


class PublicDNS:
    def __init__(self, zone_name, record_name, record_type, record_value, record_ttl):
        self._customer = "kenshoo"
        dyn_secret = 'secret'
        self._dyn_username = dyn_secret['username']
        self._dyn_password = dyn_secret['password']
        self._zone_name = zone_name
        self._record_name = record_name
        self._record_type = record_type
        self._record_value = record_value
        self._record_ttl = record_ttl
        self._fqdn = f"{self._record_name}.{self._zone_name}"

    def get_dynect_session(self):
        return DynectSession(self._customer, self._dyn_username, self._dyn_password)

    def create(self):
        dynect_session = self.get_dynect_session()
        my_zone = Zone(self._zone_name)
        my_zone.add_record(self._record_name, self._record_type, self._record_value, self._record_ttl)
        my_zone.publish()
        dynect_session.close_session()

    def delete(self):
        matched_nodes = self.__get_nodes_by_record()
        dynect_session = self.get_dynect_session()
        my_zone = Zone(self._zone_name)
        [node.delete() for node in matched_nodes]
        my_zone.publish()
        dynect_session.close_session()

import dns.update
import dns.query


DC_DNS_SERVER = "10.1.1.1"


class PrivateDNS:
    def __init__(self, zone_name, record_name, record_ttl, record_type, record_value):
        self._zone_name = zone_name
        self._record_name = record_name
        self._record_ttl = record_ttl
        self._record_type = record_type
        self._record_value = record_value

    def create(self):
        update = dns.update.Update(self._zone_name)
        update.replace(self._record_name, int(self._record_ttl), self._record_type, self._record_value)
        response = dns.query.tcp(update, DC_DNS_SERVER, timeout=10)
        print(response.to_text())

    def delete(self):
        update = dns.update.Update(self._zone_name)
        update.delete(self._record_name, self._record_type, self._record_value)
        response = dns.query.tcp(update, DC_DNS_SERVER, timeout=10)
        print(response.to_text())

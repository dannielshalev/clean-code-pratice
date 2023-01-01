from .dns.private_dns import PrivateDNS
from dns.public_dns import PublicDNS


class DNSInputs(object):
    zone_name: str
    record_name: str
    record_type: str
    record_value: str
    record_ttl: str


class DNSInputs(object):
    zone_name: str
    record_name: str
    record_type: str
    record_value: str
    record_ttl: str

    def __init__(self, zone_name, record_name, record_type, record_value, record_ttl, is_public_external_dns=False):
        self.zone_name = zone_name
        self.record_name = record_name
        self.record_type = record_type
        self.record_value = record_value
        self.record_ttl = record_ttl
        self.is_dyn_external_dns = is_public_external_dns
        self.dyn_username = 'public_secret_username'
        self.dyn_password = 'public_secret_password'
        self.customer = "danniel"
        self.ec_dns_server = '10.1.1.1'


class DNSProvider(DNSInputs):
    def __init__(self):
        self.dns_registrations = {
            'public': PublicDNS(),
            'private': PrivateDNS()
        }

    def create(self, args):
        self.dns_registrations.get(args['dns_type']).create()

    def delete(self, args):
        self.dns_registrations.get(args['dns_type']).delete()

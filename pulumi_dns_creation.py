from dyn.tm.session import DynectSession
from dyn.tm.zones import Zone, Node
from dyn.tm.errors import DynectCreateError

import dns.update
import dns.query

# A class representing the arguments that the dynamic provider needs. Each argument
# will automatically be converted from Input[T] to T before being passed to the
# functions in the provider
class Inputs(object):
    zone_name: Input[str]
    record_name: Input[str]
    record_type: Input[str]
    record_value: Input[str]
    record_ttl: Input[str]

    def __init__(self, zone_name, record_name, record_type, record_value, record_ttl, is_dyn_external_dns=False):
        self.zone_name = zone_name
        self.record_name = record_name
        self.record_type = record_type
        self.record_value = record_value
        self.record_ttl = record_ttl
        self.is_dyn_external_dns = is_public_external_dns
        dyn_secret = 'secret'
        self.dyn_username = public_secret_username
        self.dyn_password = public_secret_password
        self.customer = "danniel"
        self.ec_dns_server = '8.8.8.8'


# The code for the dynamic provider that gives us our custom resource. It handles
# all the create, read, update, and delete operations the resource needs.
class DNSProvider(Inputs):

    # The function that is called when a new resource needs to be created
    def create(self, args):
        if args['is_dyn_external_dns']:
            self.create_dyn_record(args)
        else:
            self.create_dc_record(args)

        # The creation process is finished. We assign a unique ID to this resource,
        # and return all the outputs required by the resource (in this case
        # outputs are identical to the inputs)

    def create_dyn_record(self, args):
        dynect_session = DynectSession(args['customer'], args['dyn_username'], args['dyn_password'])
        my_zone = Zone(args["zone_name"])
        try:
            my_zone.add_record(args["record_name"], args["record_type"], args["record_value"], args["record_ttl"])
            my_zone.publish()
        except DynectCreateError as e:
            print(f'The DNS {args["record_name"]}.{args["zone_name"]} already exists was not created, see: \n {e}')
        finally:
            dynect_session.close_session()

    @staticmethod
    def create_dc_record(args):
        update = dns.update.Update(args["zone_name"])
        update.replace(args["record_name"], int(args["record_ttl"]), args["record_type"], args["record_value"])
        response = dns.query.tcp(update, args['ec_dns_server'], timeout=10)
        print(response.to_text())

    # The function that is called when an existing resource needs to be deleted
    def delete(self, id, args):
        if args['is_dyn_external_dns']:
            self.delete_dyn_record(args)
        else:
            self.delete_dc_record(args)

    def delete_dyn_record(self, args):
        dynect_session = DynectSession(args['customer'], args['dyn_username'], args['dyn_password'])
        my_zone = Zone(args["zone_name"])
        my_node = Node(args["zone_name"], args["record_name"] + '.' + args["zone_name"])
        my_node.delete()
        my_zone.publish()
        dynect_session.close_session()

    @staticmethod
    def delete_dc_record(args):
        update = dns.update.Update(args["zone_name"])
        update.delete(args["record_name"], args["record_type"], args["record_value"])
        response = dns.query.tcp(update, args['ec_dns_server'], timeout=10)
        print(response.to_text())

import binascii
import os

from dyn.tm.session import DynectSession
from dyn.tm.zones import Zone, Node
from dyn.tm.errors import DynectCreateError
from pulumi import Input, Output
from pulumi.dynamic import ResourceProvider, CreateResult, DiffResult, UpdateResult, Resource

import dns.update
import dns.query

# A class representing the arguments that the dynamic provider needs. Each argument
# will automatically be converted from Input[T] to T before being passed to the
# functions in the provider
class SchemaInputs(object):
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
class SchemaProvider(ResourceProvider):

    # The function that is called when a new resource needs to be created
    def create(self, args):
        if args['is_dyn_external_dns']:
            self.create_dyn_record(args)
            return CreateResult("schema-" + binascii.b2a_hex(os.urandom(16)).decode("utf-8"), outs=args)
        else:
            self.create_dc_record(args)
            return CreateResult("schema-" + binascii.b2a_hex(os.urandom(16)).decode("utf-8"), outs=args)

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

    # The function that determines if an existing resource whose inputs were
    # modified needs to be updated or entirely replaced
    def diff(self, id, oldInputs, newInputs):
        # critical inputs that require the resource to be entirely replaced if they are modified.
        # Changes in other inputs mean the resource can be safely updated without 
        # recreating it
        replaces = []
        if (oldInputs["zone_name"] != newInputs["zone_name"]): replaces.append("zone_name")
        if (oldInputs["record_name"] != newInputs["record_name"]): replaces.append("record_name")
        if (oldInputs["record_type"] != newInputs["record_type"]): replaces.append("record_type")
        if (oldInputs["record_value"] != newInputs["record_value"]): replaces.append("record_value")
        if (oldInputs["record_ttl"] != newInputs["record_ttl"]): replaces.append("record_ttl")

        return DiffResult(
            # If the old and new inputs don't match, the resource needs to be updated/replaced
            changes=oldInputs != newInputs,
            # If the replaces[] list is empty, nothing important was changed, and we do not have to 
            # replace the resource
            replaces=replaces,
            # An optional list of inputs that are always constant
            stables=None,
            # The existing resource is deleted before the new one is created
            delete_before_replace=True)

    # The function that updates an existing resource without deleting and
    # recreating it from scratch
    def update(self, id, oldInputs, newInputs):
        # The old existing inputs are discarded and the new inputs are used
        return UpdateResult(outs={**newInputs})


# The main Schema resource that we instantiate in our infrastructure code
class Schema(Resource):
    # The inputs used by the dynamic provider are made implicitly availible as outputs 
    zone_name: Output[str]
    record_name: Output[str]
    record_type: Output[str]
    record_value: Output[str]
    record_ttl: Output[str]

    def __init__(self, name: str, args: SchemaInputs, opts=None):
        # NOTE: The args object is converted to a dictionary using vars()
        super().__init__(SchemaProvider(), name, vars(args), opts)

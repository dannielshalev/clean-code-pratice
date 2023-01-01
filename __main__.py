from dns_creation import DNSInputs, DNSProvider

if __name__ == '__main__':
    public_args = DNSInputs(zone_name='lotr.com',
                            record_name='legolas',
                            record_type='public',
                            record_value='212.143.212.143',
                            record_ttl='3600')
    public_dns = DNSProvider(public_args)

    private_args = DNSInputs(zone_name='lotr.local',
                             record_name='gollum',
                             record_type='public',
                             record_value='172.16.1.5',
                             record_ttl='3600')
    private_dns = DNSProvider(private_args)

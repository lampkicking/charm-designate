from charmhelpers.core import hookenv
from charmhelpers.contrib.network import ip
from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes


class MemcachedRequires(RelationBase):
    scope = scopes.UNIT

    @hook('{requires:memcache}-relation-joined}')
    def joined(self):
        hostname = ip.get_relation_ip(
            interface=self.conversation().relation_name
        )
        self.set_remote({
            'private-address': hostname
        })

    @hook('{requires:memcache}-relation-{joined,changed}')
    def changed(self):
        conv = self.conversation()
        conv.set_state('{relation_name}.connected')
        if conv.get_remote('host') and conv.get_remote('port'):
            # this unit's conversation has a host and port
            conv.set_state('{relation_name}.available')


    @hook('{requires:memcache}-relation-{broken,departed}')
    def broken(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.connected')
        conv.remove_state('{relation_name}.available')

    def get_remote_all(self, key, default=None):
        '''Return a list of all values presented by remote units for key'''
        values = []
        for conversation in self.conversations():
            for relation_id in conversation.relation_ids:
                for unit in hookenv.related_units(relation_id):
                    value = hookenv.relation_get(key,
                                                 unit,
                                                 relation_id) or default
                    if value:
                        values.append(value)
        return list(set(values))

    def memcache_hosts(self):
        """Return a list of memcache hosts"""
        return sorted(self.get_remote_all('private-address'))

    def memcaches(self):
        """Return a list of dicts with: host, port and udp-port"""
        memcaches = []
        for conv in self.conversations():
            memcaches.append({'host': conv.get_remote('host'),
                              'port': conv.get_remote('port'),
                              'udp-port': conv.get_remote('udp-port')})
        return memcaches

    def memcache_hosts_ports(self):
        """Return a list of tuples (host, port)"""
        return sorted((m['host'], m['port']) for m in self.memcaches())

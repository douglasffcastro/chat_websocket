$TTL 86400
@   IN  SOA     ns1.trabalhofinal.com. admin.trabalhofinal.com. (
                   2023010101
                   3600
                   1800
                   604800
                   86400
                   )

    IN  NS      ns1.trabalhofinal.com.
    IN  NS      ns2.trabalhofinal.com.

ns1     IN  A       127.0.0.1
ns2     IN  A       127.0.0.1

from scalelite import Scalelite

scalelite = Scalelite(bin_path="docker exec scalelite-api bin/rake")

servers = scalelite.list_servers()
status = scalelite.status()

print(servers)
print(status)

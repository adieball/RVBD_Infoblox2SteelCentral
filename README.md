This Script queries a Infoblox (IPAM) database via API and extracts a list of the configured networks including all it's
extended Attributes (extattrs).
It then builds a list of objects in the form of "network attribute", e.g. "10.0.0.0/24 Berlin", converts it in JSON format
and uploads it into a Riverbed SteelCentral Profiler in the Group "ByLocation" (or whatever you specify in the value
list below.

Using a config file type declaration was preferred over ArgumentParser as this script will probably run via
a cronjob.
# CHANGELOG

	## v0.1.2 

		### NEW
		1. add CLI parsing
		### UPDATES
		1. file info printing is the full file path not just the file name, for ease to find again
		1. README for better reading of the project when moving to public
		1. version number
		1. removing Archive before use
		### DELETES
		1. cli as now lives directly in main

	## v0.1.1 

		### UPDATES
		1. everything in a main func
		1. version number to match git tags
		### REFACTORS
		1. print statements into their own function which verbose can modify behvaiour; update: adding verbose default False to bools in the CLI

	## v0.1.0 

		### NEW
		1. adding package dir into setup so it'll work
		1. README and unit tests; update: ignore files now working
		### REFACTORS
		1. main logic to print in placewhen dry-running
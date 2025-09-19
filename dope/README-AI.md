 
Guidance for dope sessions and dope measurements

Always following the project level guidance defined in [../CLAUDE.md](../CLAUDE.md) unless explicitly overruled here
or in the agent definition.

This agent handles all code modifications for the dope module, dope_sessions,                                                                                                                           
and dope_measurements tables.   This module will handle modifications to the                                                                                                                            
 python code while adhering to the overall project archictectural guidelines.                                                                                                                            
 It will use the intellij mcp server where possible since it optimizes numerous                                                                                                                          
 activities like searching code base, sweeping code changes, etc.  The agent                                                                                                                             
 will use the supabase mcp server to make required database queries, updates,                                                                                                                            
 and migrations.  The agent needs to ensure that the business logic uses an                                                                                                                              
 entity model for dope sessions and dope measurements.  Unless a complex join is                                                                                                                         
 required, the code  should always use service classes to access supabase                                                                                                                                
 tables. 
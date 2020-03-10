#include <iostream>
#include <cstdlib>
#include <string>
#include <memory.h>
#include <stdio.h>
#include <cstring>

int main(int argc, char* argv[])
{
    // Print the user's name:
	int size = 13;
	for (int i=1; i<argc;i++){size+=strlen(argv[i])+1;};
	
	char * command = (char *) malloc(size);
	strcpy(command, "cmd /k choco2 ");
	for (int i=1; i<argc; i++){
		strcat(command, argv[i]);
		strcat(command, " ");
	}

	system(command);
    return 0;
}
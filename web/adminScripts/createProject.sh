#!/bin/bash
# This script will create a new Project (aka protocol)
echo
echo
echo "Creating a new Project (aka protocol)..."
echo
echo -e "Enter the \033[31mtitle\033[0m of the Project (e.g., The Project Foo) and press [ENTER]: "
read title
echo
echo -e "Enter the \033[31mid\033[0m of the Project (e.g., TheProjectFoo) and press [ENTER]: "
read id
echo
echo -e "Enter the \033[31mwg\033[0m which owns the Project (e.g., rootpi_WG) and press [ENTER]: "
read wg
echo


~/.virtualenvs/venvdj1.4/bin/python -c "import utils1_4; utils1_4.createCollectionProtocol('$title', '$id')"
echo
~/.virtualenvs/venvdj1.7/bin/python -c "import utils1_7; utils1_7.createProject('$title', '$id', '$wg')"

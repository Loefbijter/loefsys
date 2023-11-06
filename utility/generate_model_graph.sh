#!/bin/bash

WORK_DIR=../
cd $WORK_DIR

python manage.py graph_models -a -g -o infra/models.png

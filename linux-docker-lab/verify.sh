#!/bin/bash

STEP=$KATACODA_STEP

LAB_PATH="/home/ubuntu/lab"

case $STEP in

# ---------------- Linux Questions ----------------

1)
  ls $LAB_PATH | grep -q "file1.txt" && echo "done" || echo "not done"
  ;;

2)
  [ -f $LAB_PATH/test1.txt ] && echo "done" || echo "not done"
  ;;

3)
  [ -d $LAB_PATH/project ] && echo "done" || echo "not done"
  ;;

4)
  [ -f $LAB_PATH/file1_copy.txt ] && echo "done" || echo "not done"
  ;;

5)
  [ -f $LAB_PATH/dir1/file2.txt ] && echo "done" || echo "not done"
  ;;

6)
  [ ! -f $LAB_PATH/file1_copy.txt ] && echo "done" || echo "not done"
  ;;

7)
  [ -f $LAB_PATH/data.txt ] && [ $(wc -l < $LAB_PATH/data.txt) -ge 3 ] && echo "done" || echo "not done"
  ;;

8)
  [ "$(stat -c '%a' $LAB_PATH/data.txt)" = "777" ] && echo "done" || echo "not done"
  ;;


# ---------------- Docker Questions ----------------

9)
  docker ps | grep -q alpine && echo "done" || echo "not done"
  ;;

10)
  docker ps | grep -q mycontainer && echo "done" || echo "not done"
  ;;

11)
  docker ps | grep -q CONTAINER && echo "done" || echo "not done"
  ;;

12)
  ! docker ps | grep -q mycontainer && echo "done" || echo "not done"
  ;;

13)
  ! docker ps -a | grep -q mycontainer && echo "done" || echo "not done"
  ;;

14)
  docker ps | grep -q nginx && echo "done" || echo "not done"
  ;;

15)
  docker images | grep -q alpine && echo "done" || echo "not done"
  ;;


# ---------------- Final Submission ----------------

16)
  grep -q "submitted" /home/ubuntu/progress.log && echo "done" || echo "not done"
  ;;

*)
  echo "not done"
  ;;

esac
#!/usr/bin/env python
#coding:utf-8
 
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "swegui.settings")
 
import django
django.setup()
 
def main():
    from wordnn.models import WordVec
    # f = open('vectors.enwiki.top3k')
    f = open('vectors.baike.top3k')
    for line in f:
        title,vecstr = line.split('\t')
        vector = vecstr.split(' ')
        WordVec.objects.get_or_create(title=title,content=vector)
    f.close()

if __name__ == "__main__":
    main()
    print('Done!')

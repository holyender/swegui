#coding:utf-8

# Visualization tool for Semantic Word Embeddings (SWE)
# Quan Liu, USTC
# June 2015

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from .forms import AddForm
from wordnn.models import WordVec
import numpy as np
from operator import itemgetter
import random
import time


def to_str(s):
    try:
        return str(s)
    except Exception, e:
        return s.encode("utf-8")


def home(request):
    return HttpResponseRedirect("/findwordnn/")


def wordvec(request):
    if request.method == 'GET':
        word = request.GET.get("word")
        wordvec = WordVec.objects.filter(title=word).first()
    elif request.method == 'POST':
        id = request.POST.get("id")
        content = request.POST.get("content")
        content = eval(content)
        wordvec = WordVec.objects.get(id=id)
        wordvec.content = content
        wordvec.save()
    return render(request, 'wordvec.html', locals())



def findwordnn(request):

    if request.method == 'POST':
        form = AddForm(request.POST)

        submit = request.POST.get("submit", "")
        
        if form.is_valid():
            # Get the User Input Word
            if "random" in submit.lower():
                t = time.time()
                word_vecs = WordVec.objects.all()
                i = random.randint(0, word_vecs.count()-1)
                word_vec = word_vecs[i]
                userWord = word_vec.title
                print(time.time()-t)
            else:
                userWord = form.cleaned_data['word']
            userNum  = form.cleaned_data['n']
            try:
                userPtr  = WordVec.objects.get(title=userWord)
            except:
                outstr = 'Sorry, ' + to_str(userWord) + ' is now not stored in our vocabulary!'
                error = outstr
                return render(request, 'index.html', locals())
        
            userVec  = np.array(userPtr.content, dtype=float)            
            userLen  = np.sqrt(userVec.dot(userVec))
            
            wordSim = {}            
            # Find Nearest Words for Current Center Word
            if userLen != 0.0:                
                # Malloc a Dict Buffer                
                for wordPtr in WordVec.objects.all():
                    wordVec = np.array(wordPtr.content, dtype=float)
                    try:
                        dotVal  = np.dot(wordVec, userVec)
                    except:
                        continue
                    wordLen = np.sqrt(wordVec.dot(wordVec))
                    cosVal  = 0.0
                    if wordLen != 0.0:
                        cosVal = dotVal / (userLen*wordLen)
                    # Store current cosine similarity                    
                    wordSim[wordPtr.title] = cosVal

            else:
                error = "Warning, your input word vector is zero vector!"
                return render(request, 'index.html', locals())           
            
            sortNN = sorted(wordSim.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
            output = userWord + ' -> ' + to_str(userNum) + ' nearest words: '
            outNum = 0
            rs = []
            for i in sortNN:
                if cmp(to_str(i[0]), to_str(userWord)):
                    outNum = outNum + 1
                    rs.append(i)
                    if outNum == userNum:
                        break
            # return HttpResponse(to_str(output))
            max_value = rs[0][1]
            min_value = rs[-1][1]-0.1
            return render(request, 'result.html', locals())
    else:
        form = AddForm()
        
    return render(request, 'index.html', locals())



def exchange(request):
    word1 = request.REQUEST.get("word1")
    word2 = request.REQUEST.get("word2")
    wordvec1 = WordVec.objects.filter(title=word1).first()
    wordvec2 = WordVec.objects.filter(title=word2).first()
    c = wordvec1.content
    wordvec1.content = wordvec2.content
    wordvec2.content = c
    wordvec1.save()
    wordvec2.save()
    return HttpResponse("ok")


def swap(request):
    old_words = request.GET.get("old_words")
    new_words = request.GET.get("new_words")
    old_words = old_words.strip(",").split(",")
    new_words = new_words.strip(",").split(",")

    old_contents = []
    for old_word in old_words:
        old_word_vec = WordVec.objects.filter(title=old_word).first()
        old_content = old_word_vec.content
        old_contents.append(old_content)

    for new_word, old_content in zip(new_words, old_contents):
        new_word_vec = WordVec.objects.filter(title=new_word).first()
        if new_word_vec.content != old_content:
            new_word_vec.content = old_content
            new_word_vec.save()

    return HttpResponse("ok")


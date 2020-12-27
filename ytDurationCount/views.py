# i have created this file
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext
from datetime import timedelta
import datetime
import isodate
import json, requests
from urllib.parse import parse_qs, urlparse

def homePage(request):
    params = {'alert':'none'}
    return render(request, 'index.html', params)


def resultPage(request):
    if request.method == 'POST':

        def convert(time):
            ts, td = time.seconds, time.days
            th, tr = divmod(ts, 3600)
            tm, ts = divmod(tr, 60)
            ds = ''
            if td:
                ds += ' {} day{},'.format(td, 's' if td!=1 else '')
            if th:
                ds += ' {} hour{},'.format(th, 's' if th!=1 else '')
            if tm:
                ds += ' {} minute{},'.format(tm, 's' if tm!=1 else '')
            if ts:
                ds += ' {} second{}'.format(ts, 's' if ts!=1 else '')
            if ds == '':
                ds = '0 seconds'
            return ds.strip().strip(',')

        # replace with your api
        api_key = 'AIzaSyCgQy3L9bVQMF4IF96Y1nVEDe5zDFVZofI' 
        # replace with your playlist_id
        playlist_url = request.POST.get('playlistLink', 'default')
        try:
            query = parse_qs(urlparse(playlist_url).query, keep_blank_values=True)
            playlist_id = query["list"][0]
        except:
            params = {'alert': 'block'}
            return render(request, 'index.html', params)
        # playlist_id = 'PLwgFb6VsUj_mtXvKDupqdWB2JBiek8YPB'

        PlaylistURL1 = 'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&fields=items/contentDetails/videoId,nextPageToken&key={}&playlistId={}&pageToken='.format(api_key, playlist_id)
        PlaylistURL2 = 'https://www.googleapis.com/youtube/v3/videos?&part=contentDetails&key={}&id={}&fields=items/contentDetails/duration'.format(api_key, '{}')

        next_page = ''
        count = 0
        duration = timedelta(0)

        while True:
            video_list = [] 

            results = json.loads(requests.get(PlaylistURL1 + next_page).text)
            
            for i in results['items']:
                video_list.append(i['contentDetails']['videoId'])
                
            url_list = ','.join(video_list)
            count += len(video_list)

            site_json = json.loads(requests.get(PlaylistURL2.format(url_list)).text)
            for i in site_json['items']:
                duration += isodate.parse_duration(i['contentDetails']['duration'])

            if 'nextPageToken' in results:
                next_page = results['nextPageToken']
            else:
                avg_time = convert(duration/count)
                total_length = convert(duration)
                length_at_25 = convert(duration/1.25)
                length_at_5 = convert(duration/1.5)
                length_at_75 = convert(duration/1.75)
                length_at_2 = convert(duration/2)
                break

        params = {'total_video':count, 'avg_time':avg_time, 'total_length':total_length, 'length_at_25':length_at_25, 'length_at_5':length_at_5, 'length_at_75':length_at_75, 'length_at_2':length_at_2}
        return render(request, 'result.html', params)
    else:
        return redirect('homePage')

# Error Handler

def handle404(request, *args, **argv):
    params = {'alert':'none'}
    # return render(request, 'index.html', params, status=404)
    return redirect('homePage', params)

def handle500(request):
    params = {'alert':'none'}
    # return render(request, 'index.html', params, status=404)
    return redirect('homePage')
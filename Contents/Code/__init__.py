RT_IMDB_SEARCH_URL = 'http://www.rottentomatoes.com/alias?type=imdbid&s=%s'
RT_API_BASE = 'http://api.rottentomatoes.com/api/public/v1.0/%s?apikey=twdg3rv2zeesn29thmx58sky%s'

def Start():
  HTTP.CacheTime = CACHE_1DAY

class RottenTomatoesAgent(Agent.Movies):
  name = 'Rotten Tomatoes'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.imdb']
  
  def search(self, results, media, lang):
    imdb_id = media.primary_metadata.id.replace('tt', '')
    results.Append(MetadataSearchResult(id=imdb_id, score=100))
  
  def update(self, metadata, media, lang):
    try: movie_page = HTML.ElementFromURL(RT_IMDB_SEARCH_URL % metadata.id)
    except: return
    rtID = movie_page.xpath('//div[@id="all"]')[0].get('movie')
    rtMovie = JSON.ObjectFromURL(RT_API_BASE % ('movies/' + rtID + '.json', ''))
    #Log(str(rtMovie))
    #get ratings
    if Prefs['get_rating']:
      if Prefs['rating_type'] == 'Tomatometer':
        try: metadata.rating = float(rtMovie['ratings']['critics_score'])/10
        except:
          try: metadata.rating = float(rtMovie['ratings']['audience_score'])/10
          except: pass
      else:
        try: metadata.rating = float(rtMovie['ratings']['audience_score'])/10
        except:
          try: metadata.rating = float(rtMovie['ratings']['critics_score'])/10
          except: pass
    #get genres
    metadata.genres.clear()
    if Prefs['get_genres']:
      for g in rtMovie['genres']:
        metadata.genres.add(g)
    #get summary
    if Prefs['get_summary']:
      if len(rtMovie) > 0:
        metadata.summary = rtMovie['synopsis']
    #get poster
    if Prefs['get_poster']:
      poster = rtMovie['posters']['original']
      if poster not in metadata.posters:
        metadata.posters[poster] = Proxy.Media(HTTP.Request(poster))
    #get mpaa rating
    if Prefs['get_contentrating']:
      metadata.content_rating = rtMovie['mpaa_rating']
    #get abridged directors
    if Prefs['get_directors']:
      metadata.directors.clear()
      for d in rtMovie['abridged_directors']:
        metadata.directors.add(d['name'])
    #get abridged cast
    if Prefs['get_abridged_cast']:
      metadata.roles.clear()
      for c in rtMovie['abridged_cast']:
        role = metadata.roles.new()
        role.role = c['characters'][0]
        role.actor = c['name']
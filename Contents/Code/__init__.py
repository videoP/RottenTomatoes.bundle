RT_API_KEY = 'gr66mbcjxezddama5w3vaxcb'
RT_ALIAS_URL = 'http://rt.plex.tv/api/public/v1.0/movie_alias.json?id=%s&type=imdb&apikey=' + RT_API_KEY

def Start():
	HTTP.CacheTime = CACHE_1WEEK

class RottenTomatoesAgent(Agent.Movies):

	name = 'Rotten Tomatoes'
	languages = [Locale.Language.English]
	primary_provider = False
	contributes_to = ['com.plexapp.agents.imdb']

	def search(self, results, media, lang):

		if media.primary_metadata:
			results.Append(MetadataSearchResult(
				id = media.primary_metadata.id,
				score = 100
			))

	def update(self, metadata, media, lang):

		try:
			rt_movie = JSON.ObjectFromURL(RT_ALIAS_URL % (metadata.id.strip('t')), sleep=2.0)
		except:
			return None

		if 'error' in rt_movie:
			return None

		# get ratings
		if Prefs['get_rating']:
			if Prefs['rating_type'] == 'Tomatometer':
				rating = rt_movie['ratings']['critics_score']
			else:
				rating = rt_movie['ratings']['audience_score']

			if rating is not None and rating > 0:
				metadata.rating = float(rating)/10
			else:
				metadata.rating = None
		else:
			metadata.rating = None

		# get genres
		metadata.genres.clear()
		if Prefs['get_genres']:
			for g in rt_movie['genres']:
				metadata.genres.add(g)

		# get poster
		poster = rt_movie['posters']['original']
		del metadata.posters[poster] # Make sure we remove any old, previously downloaded small poster (*_tmb.jpg)

		poster = poster.replace('_tmb.jpg', '_xxl.jpg')

		if Prefs['get_poster']:
			if poster not in metadata.posters:
				metadata.posters[poster] = Proxy.Media(HTTP.Request(poster))
		else:
			del metadata.posters[poster]

		# get mpaa rating
		if Prefs['get_contentrating']:
			metadata.content_rating = rt_movie['mpaa_rating']
		else:
			metadata.content_rating = None

		# get directors
		metadata.directors.clear()
		if Prefs['get_directors']:
			for d in rt_movie['abridged_directors']:
				metadata.directors.add(d['name'])

		# get cast
		metadata.roles.clear()
		if Prefs['get_abridged_cast']:
			for c in rt_movie['abridged_cast']:
				role = metadata.roles.new()
				try: role.role = c['characters'][0]
				except: role.role = c['name']
				role.actor = c['name']

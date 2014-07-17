RT_API_BASE = 'http://rt.plex.tv/api/public/v1.0/%s?apikey=gr66mbcjxezddama5w3vaxcb%s'

def Start():
	HTTP.CacheTime = CACHE_1WEEK

class RottenTomatoesAgent(Agent.Movies):
	name = 'Rotten Tomatoes'
	languages = [Locale.Language.English]
	primary_provider = False
	contributes_to = ['com.plexapp.agents.imdb']

	def search(self, results, media, lang):
		imdb_id = media.primary_metadata.id.strip('t')
		rtSearch = JSON.ObjectFromURL(RT_API_BASE % ('movie_alias.json', '&type=imdb&id=' + imdb_id), sleep=2.0)

		if 'error' not in rtSearch:
			results.Append(MetadataSearchResult(id=str(rtSearch['id']), score=100))

	def update(self, metadata, media, lang):
		rtMovie = JSON.ObjectFromURL(RT_API_BASE % ('movies/' + metadata.id + '.json', ''), sleep=2.0)

		# get ratings
		if Prefs['get_rating']:
			if Prefs['rating_type'] == 'Tomatometer':
				rating = rtMovie['ratings']['critics_score']
			else:
				rating = rtMovie['ratings']['audience_score']

			if rating is not None and rating > 0:
				metadata.rating = float(rating)/10
			else:
				metadata.rating = None
		else:
			metadata.rating = None

		# get genres
		metadata.genres.clear()
		if Prefs['get_genres']:
			for g in rtMovie['genres']:
				metadata.genres.add(g)

		# get poster
		poster = rtMovie['posters']['original']
		if Prefs['get_poster']:
			if poster not in metadata.posters:
				metadata.posters[poster] = Proxy.Media(HTTP.Request(poster))
		else:
			del metadata.posters[poster]

		# get mpaa rating
		if Prefs['get_contentrating']:
			metadata.content_rating = rtMovie['mpaa_rating']
		else:
			metadata.content_rating = None

		# get directors
		metadata.directors.clear()
		if Prefs['get_directors']:
			for d in rtMovie['abridged_directors']:
				metadata.directors.add(d['name'])

		# get cast
		metadata.roles.clear()
		if Prefs['get_abridged_cast']:
			for c in rtMovie['abridged_cast']:
				role = metadata.roles.new()
				try: role.role = c['characters'][0]
				except: role.role = c['name']
				role.actor = c['name']

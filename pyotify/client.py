import json
import requests
import pyotify.utils as utils
import pyotify.auth as auth


class Spotify:
    '''Web API Reference

    https://developer.spotify.com/documentation/web-api/reference/
    '''
    _api_prefix = 'https://api.spotify.com/v1/'
    max_retries = 10
    api_call_timeout = None

    def __init__(self, client_id, client_secret, redirect_uri=None, state=None,
                 scope=None, show_dialog=False, cached_token_path=None):

        self._session = requests.Session()
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = auth.SpotifyClientCredentialsAuth(self._session, client_id, client_secret).get_access_token()
        self.redirect_uri = redirect_uri
        self.state = state
        self.scope = utils.normalize_scope(scope) if scope else None
        self.show_dialog = show_dialog
        # self.cached_token_path = self.cached_token_path or f'.spotify_cached_token_{client_id}.json'

    def _get_authorization_headers(self):
        return {'Authorization': f'Bearer {self.token}'}

    def _api_call(self, method, url, request=None, **kwargs):
        url = self._api_prefix + url

        headers = self._get_authorization_headers()

        response = self._session.request(method=method, url=url, headers=headers, **kwargs)

        response.raise_for_status()

        if response.content == b'':
            return (f'REQUEST {request} OK!')

        return response.json()

    def _get(self, url, **kwargs):
        return self._api_call(method='GET', url=url, **kwargs)

    def _post(self, url, **kwargs):
        return self._api_call(method='POST', url=url, **kwargs)

    def _put(self, url, **kwargs):
        return self._api_call(method='PUT', url=url, **kwargs)

    def _delete(self, url, **kwargs):
        return self._api_call(method='DELETE', url=url, **kwargs)

    def me(self):
        return self._get('me')

    def user_profile(self, user_id=None):
        if user_id is None:
            self.me()
        return self._get(f'users/{user_id}')

    def search(self, q, type, market=None, limit=None, offset=None, include_external=None):
        params = {'q':q, 'type':type, 'market':market, 'limit':limit, 'offset':offset, 'include_external':include_external}
        return self._get('search', params=params)

    def albums(self, ids, market=None):
        params = {'ids':ids, 'market':market}
        return self._get('albums', params=params)

    def album_tracks(self, id, limit=None, offset=None, market=None):
        params = {'limit':limit, 'offset':offset, 'market':market}
        return self._get(f'albums/{id}/tracks', params=params)

    def artists(self, ids):
        params = {'ids':ids}
        return self._get('artists', params=params)

    def artists_albums(self, id, include_groups=None, country=None, limit=None, offset=None):
        params = {'include_groups':include_groups, 'country':country, 'limit':limit, 'offset':offset}
        return self._get(f'artists/{id}/albums', params=params)

    def artists_top_tracks(self, id, country=None):
        params = {'country':country}
        return self._get(f'artists/{id}/top-tracks', params=params)

    def related_artists(self, id):

        return self._get(f'artists/{id}/related-artists')

    def categories(self, category_id=None, country=None, locale=None, limit=None, offset=None):

        if category_id is None:
            params = {'country':country, 'locale':locale, 'limit':limit, 'offset':offset}
            return self._get(f'browse/categories', params=params)
        params = {'country':country, 'locale':locale}
        return self._get(f'browse/categories/{category_id}', params=params)

    def category_playlists(self, category_id, country=None, limit=None, offset=None):
        params = {'country':country, 'limit':limit, 'offset':offset}
        return self._get(f'browse/categories/{category_id}/playlists', params=params)

    def featured_playlists(self, locale=None, country=None, timestamp=None, limit=None, offset=None):
        params = {'locale':locale, 'country':country, 'timestamp':timestamp, 'limit':limit, 'offset':offset}
        return self._get(f'browse/featured-playlists', params=params)

    def new_releases(self, country=None, limit=None, offset=None):
        params = {'country':country, 'limit':limit, 'offset':offset}
        return self._get(f'browse/new-releases', params=params)

    def recommendations(self, limit=None, market=None, seed_artists=None, seed_genres=None, seed_tracks=None, **kwargs):
        params = {'limit':limit,
                  'market':market,
                  'seed_artists':seed_artists,
                  'seed_genres':seed_genres,
                  'seed_tracks':seed_tracks,
                  **kwargs}
        return self._get('recommendations', params=params)

    def user_follows_artists(self, ids):
        params = {'type':'artist', 'ids':ids}
        return self._get('me/following/contains', params=params)

    def user_follows_users(self, ids):
        params = {'type':'user', 'ids':ids}
        return self._get('me/following/contains', params=params)

    def user_follows_playlist(self, playlist_id, ids):
        params = {'ids':ids}
        return self._get(f'playlists/{playlist_id}/followers/contains', params=params)

    def follow_artists(self, ids):
        params = {'type':'artist', 'ids':','.join(ids)}
        return self._put('me/following', params=params, request='follow_artist')

    def follow_users(self, ids):
        params = {'type':'user', 'ids':','.join(ids)}
        return self._put('me/following', params=params, request='follow_user')

    def follow_playlist(self, playlist_id, public=True):
        params = {'public': public}
        return self._put(f'playlists/{playlist_id}/followers', params=params, request='follow_playlist')

    def user_followed_artists(self, limit=None, after=None):
        params = {'limit':limit, 'after':after, 'type':'artist'}
        return self._get('me/following', params=params)

    def unfollow_artists(self, ids):
        params = {'ids':','.join(ids), 'type':'artist'}
        return self._delete('me/following', params=params, request='unfollow_artist')

    def unfollow_users(self, ids):
        params = {'ids':','.join(ids), 'type':'user'}
        return self._delete('me/following', params=params, request='unfollow_user')

    def unfollow_playlist(self, playlist_id):

        return self._delete(f'playlists/{playlist_id}/followers', request='unfollow_playlist')

    def top_artists(self, type='artists', limit=None, offset=None, time_range=None):
        params = {'limit':limit, 'offset':offset, 'time_range':time_range}
        return self._get(f'me/top/{type}', params=params)

    def top_tracks(self, type='tracks', limit=None, offset=None, time_range=None):
        params = {'limit':limit, 'offset':offset, 'time_range':time_range}
        return self._get(f'me/top/{type}', params=params)

    def audio_analysis(self, id):

        return self._get(f'audio-analysis/{id}')

    def audio_features(self, ids):

        return self._get(f'audio-features', ids=ids)

    def tracks(self, ids, market=None):
        params = {'ids':ids, 'market':market}
        return self._get('tracks', params=params)

    def add_track_to_playlist(self, playlist_id, uris=None, position=None):
        params = {'uris':uris, 'position':position}
        return self._post(f'playlists/{playlist_id}/tracks', params=params, request='add_track_to_playlist')

    def change_playlist_details(self, playlist_id, name=None, public=None, collaborative=None, description=None):
        params = {'name':name, 'public':public, 'collaborative':collaborative, 'description':description}
        return self._put(f'playlists/{playlist_id}', params=params, request='change_playlist_details')

    def create_playlist(self, user_id, name, public=True, collaborative=False, description=None):
        pass

    def my_playlists(self, limit=None, offset=None):
        params = {'limit':limit, 'offset':offset}
        return self._get('me/playlists', params=params)

    def user_playlists(self, user_id=None, limit=None, offset=None):
        params = {'limit': limit, 'offset': offset}
        if user_id is None:
            self.my_playlists(params)
        return self._get(f'users/{user_id}/playlists', params=params)

    def playlist_cover_image(self, playlist_id):

        return self._get(f'playlists/{playlist_id}/images')

    def playlist(self, playlist_id, fields=None, market=None):
        params = {'fields':fields, 'market':market}
        return self._get(f'playlists/{playlist_id}', params=params)

    def playlist_tracks(self, playlist_id, fields=None, limit=None, offset=None, market=None):
        params = {'fields':fields, 'limit':limit, 'offset':offset, 'market':market}
        return self._get(f'playlists/{playlist_id}/tracks', params=params)

    def remove_occurences_of_specific_tracks(self, playlist_id, *args, snapshot_id=None):
        if isinstance(args[0], tuple):
            body = {"tracks": [{"uri": f"spotify:track:{arg[0]}", "positions": arg[1:]} for arg in args]}
            request = 'remove_specific_occurrence_of_track'
        else:
            body = {"tracks":[{"uri": f"spotify:track:{arg}"} for arg in args]} if len(args) > 1 else {"tracks": [{"uri": f"spotify:track:{args[0]}"}]}
            request = 'remove_all_occurrences_of_specific_tracks'
        if snapshot_id:
            body['snapshot_id'] = snapshot_id
            request = 'remove_specific_occurence_of_track_in_specific_playlist_snapshot'
        data = json.dumps(body)
        return self._delete(f'playlists/{playlist_id}/tracks', data=data, request=request)

    def reorder_playlist_tracks(self, playlist_id, range_start, insert_before, range_length=1, snapshot_id=None):
        body = {"range_start": range_start, "insert_before": insert_before, "range_length": range_length}
        if snapshot_id:
            body['snapshot_id'] = snapshot_id
        data = json.dumps(body)
        return self._put(f'playlists/{playlist_id}/tracks', data=data, request='reorder_playlist_tracks')

    def replace_playlist_tracks(self, playlist_id, *args):
        body = {"uris": [f"spotify:track:{arg}" for arg in args]}
        data = json.dumps(body)
        return self._put(f'playlists/{playlist_id}/tracks', data=data, request='replace_playlist_tracks')

    def upload_custom_playlist_cover_image(self, playlist_id, image_path):
        data = utils.encode_image(image_path)
        return self._put(f'playlists/{playlist_id}/images', data=data, request='upload_custom_playlist_cover_image')

    def saved_albums_contains(self, ids):
        params = {'ids':ids}
        return self._get('me/albums/contains', params=params)

    def saved_tracks_contains(self, ids):
        params = {'ids': ids}
        return self._get('me/tracks/contains', params=params)

    def saved_albums(self, limit=None, offset=None, market=None):
        params = {'limit':limit, 'offset':offset, 'market':market}
        return self._get('me/albums', params=params)

    def saved_tracks(self, limit=None, offset=None, market=None):
        params = {'limit':limit, 'offset':offset, 'market':market}
        return self._get('me/tracks', params=params)

    def remove_saved_albums(self, ids):
        params = {'ids':','.join(ids)}
        return self._delete('me/albums', params=params, request='remove_user_saved_albums')

    def remove_saved_tracks(self, ids):
        params = {'ids':','.join(ids)}
        return self._delete('me/tracks', params=params, request='remove_user_saved_tracks')

    def save_albums(self, ids):
        params = {'ids':','.join(ids)}
        return self._put('me/albums', params=params, request='save_albums_for_current_user')

    def save_tracks(self, ids):
        params = {'ids': ','.join(ids)}
        return self._put('me/tracks', params=params, request='save_tracks_for_current_user')

    def available_devices(self):

        return self._get('me/player/devices')

    def current_playback(self, market=None):
        params = {'market':market}
        return self._get('me/player', params=params)

    def recently_played(self, limit=None, after=None, before=None):
        params = {'limit':limit, 'after':after, 'before':before}
        return self._get('me/player/recently-played', params=params)

    def currently_playing(self, market=None):
        params = {'market':market}
        return self._get('me/player/currently-playing', params=params)

    def pause(self, device_id=None):
        params = {'device_id':device_id}
        return self._put('me/player/pause', params=params, request='pause')

    def seek(self, position_ms, device_id=None):
        params = {'position_ms':position_ms, 'device_id':device_id}
        return self._put('me/player/seek', params=params, request='seek')

    def repeat(self, state, device_id=None):
        params = {'state':state, 'device_id':device_id}
        return self._put('me/player/repeat', params=params, request='repeat')

    def volume(self, volume_percent, device_id=None):
        params = {'volume_percent':volume_percent, 'device_id':device_id}
        return self._put('me/player/volume', params=params, request='volume')

    def next_track(self, device_id=None):
        params = {'device_id':device_id}
        return self._post('me/player/next', params=params, request='next_track')

    def previous_track(self, device_id=None):
        params = {'device_id':device_id}
        return self._post('me/player/previous', params=params, request='previous_track')

    def play(self, device_id=None):
        params = {'device_id':device_id}
        return self._put('me/player/play', params=params, request='play')

    def shuffle(self, state, device_id=None):
        params = {'state':state, 'device_id':device_id}
        return self._put('me/player/shuffle', params=params, request='shuffle')

    def transfer(self, device_ids, play=None):
        params = {'device_ids':device_ids, 'play':play}
        return self._put('me/player', params=params, request='transfer')

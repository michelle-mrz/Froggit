"""
Sound classes for 2D game support.

This classes wrap the Kivy audio interface, making it simpler for students to use.

Author: Walker M. White (wmw2)
Date:   August 1, 2017 (Python 3 version)
"""
from kivy.core.audio import SoundLoader
from .app import GameApp


class Sound(object):
    """
    A class representing a sound object that can be played.
    
    A sound is a WAV file that can be played on command via the method :meth:`play`.  
    While some platforms may support MP3s, we can only guarantee that WAVs work on all 
    platforms. In order for Kivy to find a WAV or MP3 file, you should put it in the
    **Sounds** directory.  Sounds in that folder can be referenced directly by name.
    
    When a sound is played, it cannot be played again until it finishes, or is stopped.  
    This means that if you want multiple, simultaneous sound effects from the same WAV 
    file.you will need to create multiple Sound objects.
    """
    # This class is a simply replacement for the built-in Kivy Sound class.  It is a
    # little better with error handling, since GStreamer appears to be quite unreliable.
    
    # MUTABLE PROPERTIES
    @property
    def volume(self):
        """
        The current sound volume.
        
        1 means full volume, 0 means mute.  The default value is 1.
        
        **Invariant**: Must float in the range 0..1.
        """
        return self._sound.volume
    
    @volume.setter
    def volume(self,value):
        assert type(value) in [int, float] and value >= 0 and value <= 1, \
            'value %s is not a valid volume' % repr(value)
        self._sound.volume = value
    
    # IMMUTABLE PROPERTIES
    @property
    def source(self):
        """
        The source file for this sound. 
        
        **Immutable**: This value cannot be changed after the sound is loaded.
        
        **Invariant**: Must be a nonempty string.
        """ 
        return self._source
    
    @property
    def playing(self):
        """
        Whether or not the sound is currently playing.
        
        **Immutable**: This value cannot be changed.  You should use the :meth:`play` 
        and :meth:`stop` methods to alter its value.
        
        **Invariant**: Must be a boolean.
        """ 
        return self._sound.state == 'play'
    
    def __init__(self,source):
        """
        Creates a new sound from a file.
        
        :param source: The string providing the name of a sound file
        :type source:  ``str``
        """
        from .app import GameApp
        assert GameApp.is_sound(source), 'source %s is not a sound file' % repr(source)
        self._source = source
        self._sound  = SoundLoader.load(source)
        self._sound.load()
        if self._sound is None:
            raise IOError('Module game2d cannot read the file %s' % repr(source))
    
    def play(self,loop=False):
        """
        Plays this sound.
        
        The sound will play until completion, or interrupted by the user.
        
        :param loop: Whether or not to loop the sound
        :type loop:  ``bool``
        """
        self._sound.loop = loop
        self._sound.play()

    def stop(self):
        """
        Stops this sound.
        
        This will stop the sound immediately, even if it is looping.
        """
        self._sound.stop()


# #mark -
class SoundLibrary(object):
    """
    A class abstracting a dictionary that maps keys to Sound objects.
    
    This class implements to the dictionary interface to make it easier to load
    sounds and manage them.  To load a sound, simply assign it to the library
    object, as follows::
        
        soundlib['soundname'] = 'soundfile.wav'
    
    The sound library will load the sound and map it to 'soundname' as the key.
    To play the sound, we access it as follows::
        
        soundlib['soundname'].play()
    """
    
    def __init__(self):
        """
        Creates a new, empty sound library.
        """
        self._data = {}
    
    def __len__(self):
        """
        :return: The number of sounds in this library.
        :rtype:  ``int`` >= 0
        """
        return len(self._data)
    
    def __getitem__(self, key):
        """
        Accesses the sound object for the given name.
        
        :param key: The key identifying a sound object
        :type key:   ``str``
        
        :return: The object for the given sound name.
        :rtype:  :class:`Sound`
        """
        return self._data[key]
    
    def __setitem__(self, key, filename):
        """
        Creates a sound object from the file filename and assigns it the given name.
        
        :param key: The key identifying a sound object
        :type key:  ``str``
        
        :param filename: The name of the file containing the sound source
        :type filename:  ``str``
        """
        self._data[key] = Sound(filename)
    
    def __delitem__(self, key):
        """
        Deletes the Sound object for the given sound name.
        
        :param key: The key identifying a sound object
        :type key:  ``str``
        """
        del self._data[key]
    
    def __iter__(self):
        """
        :return: The iterator for this sound dictionary.
        :rtype:  ``iterable``
        """
        return iter(self._data.keys())
    
    def keys(self):
        """
        :return: The keys for this sound dictionary.
        :rtype:  ``iterable``
        """
        return self._data.keys()

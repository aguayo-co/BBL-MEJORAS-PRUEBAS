from wagtail.embeds.oembed_providers import youtube

youtube_custom_provider = youtube
youtube_custom_provider["endpoint"] = "https://www.youtube.com/oembed"

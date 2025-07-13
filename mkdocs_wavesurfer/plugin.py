import mkdocs
import re
from bs4 import BeautifulSoup as BS

class WaveConfig(mkdocs.config.base.Config):
    # as per https://wavesurfer.xyz/docs/types/wavesurfer.WaveSurferOptions
    height = mkdocs.config.config_options.Type(int, default=128)
    width = mkdocs.config.config_options.Type(int | str, default='100%')
    splitChannels = mkdocs.config.config_options.Type(bool, default=False)
    normalize = mkdocs.config.config_options.Type(bool, default=False)
    waveColor = mkdocs.config.config_options.Type(str, default='#ff4e00')
    progressColor = mkdocs.config.config_options.Type(str, default='#dd5e98')
    cursorColor = mkdocs.config.config_options.Type(str, default='#ddd5e9')
    cursorWidth = mkdocs.config.config_options.Type(int, default=2)
    barWidth = mkdocs.config.config_options.Type(int | float, default=float('nan'))
    barGap = mkdocs.config.config_options.Type(int | float, default=float('nan'))
    barRadius = mkdocs.config.config_options.Type(int | float, default=float('nan'))
    barHeight = mkdocs.config.config_options.Type(int | float, default=float('nan'))
    barAlign = mkdocs.config.config_options.Choice(['top', 'bottom', ''], default='')
    minPxPerSec = mkdocs.config.config_options.Type(int, default=1)
    fillParent = mkdocs.config.config_options.Type(bool, default=True)
    autoplay = mkdocs.config.config_options.Type(bool, default=False)
    interact = mkdocs.config.config_options.Type(bool, default=True)
    dragToSeek = mkdocs.config.config_options.Type(bool, default=False)
    hideScrollbar = mkdocs.config.config_options.Type(bool, default=False)
    audioRate = mkdocs.config.config_options.Type(float, default=1.0)
    autoScroll = mkdocs.config.config_options.Type(bool, default=True)
    autoCenter = mkdocs.config.config_options.Type(bool, default=True)
    sampleRate = mkdocs.config.config_options.Type(int, default=8000)

class Wave(mkdocs.plugins.BasePlugin[WaveConfig]):
    def on_config(self, config):
        # Build JS options from config
        js_options = {
            'height': self.config['height'],
            'width': f"'{self.config['width']}'" if isinstance(self.config['width'], str) else self.config['width'],
            'splitChannels': str(self.config['splitChannels']).lower(),
            'normalize': str(self.config['normalize']).lower(),
            'waveColor': f"'{self.config['waveColor']}'",
            'progressColor': f"'{self.config['progressColor']}'",
            'cursorColor': f"'{self.config['cursorColor']}'",
            'cursorWidth': self.config['cursorWidth'],
            'barWidth': 'NaN' if self.config['barWidth'] != self.config['barWidth'] else self.config['barWidth'],
            'barGap': 'NaN' if self.config['barGap'] != self.config['barGap'] else self.config['barGap'],
            'barRadius': 'NaN' if self.config['barRadius'] != self.config['barRadius'] else self.config['barRadius'],
            'barHeight': 'NaN' if self.config['barHeight'] != self.config['barHeight'] else self.config['barHeight'],
            'barAlign': f"'{self.config['barAlign']}'",
            'minPxPerSec': self.config['minPxPerSec'],
            'fillParent': str(self.config['fillParent']).lower(),
            'autoplay': str(self.config['autoplay']).lower(),
            'interact': str(self.config['interact']).lower(),
            'dragToSeek': str(self.config['dragToSeek']).lower(),
            'hideScrollbar': str(self.config['hideScrollbar']).lower(),
            'audioRate': self.config['audioRate'],
            'autoScroll': str(self.config['autoScroll']).lower(),
            'autoCenter': str(self.config['autoCenter']).lower(),
            'sampleRate': self.config['sampleRate'],
        }
        # Build JS config string
        options_str = ',\n  '.join(f"{k}: {v}" for k, v in js_options.items())
        js_config = f"const options = {{\n  {options_str}\n}};\n"
        config['ws_config_obj'] = js_config
        return config
    
    def on_post_page(self, output, page, config):
        soup = BS(output, 'html.parser')
        
        # Find all audio-container divs
        # Get the file path from the contained audio source element
        # Add a wavesurfer script element to the list
        surfers_data = []
        for div in soup.find_all(class_='audio-container'):
            #for source_el in div.find_ass(src=True):
            #    surfers_data.append((div['id'], div.find('audio')['id'], source_el['src']))
            surfers_data.append((div['id'], div.find('audio')['id'], div.find('source')['src']))

        js = config['ws_config_obj']
        for container_id, audio_id, src_path in surfers_data:
            num = re.search(r'\d+', container_id).group(0)
            js += f"""
surfer{num} = WaveSurfer.create({{ ...options, ...{{
    container: document.querySelector('#{container_id}'),
    media: document.querySelector('#{audio_id}'),
    url: '{src_path}',
}} }})
surfer{num}.on('click', () => {{
    surfer{num}.play()
}})
"""
        if surfers_data:
            surfer_script = soup.new_tag('script')
            surfer_script.string = f"""
function initSurfers() {{
{js}
}});
"""
#window.addEventListener('load', event => {{
            soup.body.append(surfer_script)

            lib_script= soup.new_tag('script')
            lib_script['src'] = "https://unpkg.com/wavesurfer.js@7"
            lib_script['onload'] = "initSurfers()"
            soup.body.append(lib_script)


        return str(soup)

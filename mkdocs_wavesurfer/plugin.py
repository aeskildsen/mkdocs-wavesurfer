import mkdocs
import re
import xml.etree.ElementTree as ET
import uuid

class Wave(mkdocs.plugins.BasePlugin):
    config_scheme = (
        ('autoplay', mkdocs.config.config_options.Type(bool, default=False)),
        ('controls', mkdocs.config.config_options.Type(bool, default=True)),
        ('loop', mkdocs.config.config_options.Type(bool, default=False)),
        ('muted', mkdocs.config.config_options.Type(bool, default=False)),
        ('preload', mkdocs.config.config_options.Type(str, default='metadata')),
        ('width', mkdocs.config.config_options.Type(str, default='100%'))
    )

    
    def on_post_page(self, output, page, config):
        audio_elements = re.finditer(r'(<audio.+?</audio>)+', output, re.M | re.DOTALL)
        scripts = ''

        if audio_elements:
            # load wavesurfer script
            output = output.replace('</head>', '<script src="https://unpkg.com/wavesurfer.js@7"></script></head>')
            num = 0
            for match in audio_elements:
                id = f"wavesurfer{num}"
                audiotag = match.group(0)

                src = re.search(r'src=\"(.+?)\"', audiotag)
                if src:
                    url = src.group(1)
                    scripts += f"""<script defer>
                            console.log('{id}')
                            const {id} = WaveSurfer.create({{
                            container: '#{id}',
                            waveColor: 'rgb(200, 0, 200)',
                            progressColor: 'rgb(100, 0, 100)',
                            url: '{url}',
                        }})

                        {id}.on('click', () => {{
                            {id}.play()
                        }})
                        </script>"""
                    contained_tag = f'<div id="{id}">' + audiotag + '</div>'
                    output = output.replace(audiotag, contained_tag)

                num += 1
            
            output = output.replace('</head>', scripts + '</head>')
        
        return output

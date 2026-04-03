#!/usr/bin/env python3
# nicegui_app.py - EchoBreaker with NiceGUI (fixed version, fully English)

import asyncio
from pathlib import Path
import tempfile
import logging

import sys

# Add project root to sys.path so it can find the 'services' library
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from nicegui import ui

# Service imports - adjust paths if needed
try:
    from services.youtube.downloader import YouTubeDownloader
    from services.audio.transcription import TranscriptionService
    from services.reasoning.generator import ReasoningEngine
    from services.search.youtube_search import SearchService
    from core.config import Config
except ImportError as e:
    print(f"Import error: {e}")
    print("Suggestions:")
    print("  1. Move nicegui_app.py to project root")
    print("  2. Or add project root to sys.path:")
    print("     import sys; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory result storage
analysis_result = {
    'transcript': '',
    'claims': [],
    'counters': [],
    'opposing_videos': [],
    'status': 'Ready',
}

@ui.page('/')
async def main_page():
    ui.dark_mode().enable()

    with ui.header().classes('items-center px-4 py-3 bg-gray-900 text-white shadow'):
        ui.label('EchoBreaker').classes('text-2xl font-bold')
        ui.space()
        ui.label('Break YouTube echo chambers locally').classes('text-sm opacity-70')

    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-8'):
        ui.markdown('### Enter a YouTube video URL to analyze')

        url_input = ui.input(
            label='YouTube URL',
            placeholder='https://www.youtube.com/watch?v=...'
        ).props('outlined clearable rounded dense').classes('w-full max-w-3xl')

        status_label = ui.label('Status: Ready').classes('text-lg font-medium mt-2')
        progress = ui.linear_progress(value=0).props('instant').classes('w-full mt-3')
        progress.visible = False

        result_card = ui.card().classes('w-full mt-6 p-6 bg-gray-800 rounded-xl shadow-xl').style('min-height: 500px;')

        async def analyze_video():
            url = url_input.value.strip()
            if not url or 'youtube.com' not in url:
                ui.notify('Please enter a valid YouTube URL', type='warning', position='top')
                return

            progress.visible = True
            progress.value = 0
            status_label.text = 'Status: Starting analysis...'

            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    status_label.text = 'Downloading audio...'
                    progress.value = 0.15
                    downloader = YouTubeDownloader(output_dir=tmp_dir)
                    audio_path_str, metadata = await asyncio.to_thread(downloader.download_audio_with_metadata, url)
                    audio_path = Path(audio_path_str)

                    status_label.text = 'Transcribing audio...'
                    progress.value = 0.35
                    transcriber = TranscriptionService()
                    transcript = await transcriber.transcribe_file(str(audio_path))
                    analysis_result['transcript'] = transcript

                    status_label.text = 'Analyzing video and generating counter-arguments...'
                    progress.value = 0.55
                    reasoning_engine = ReasoningEngine()
                    # We pass a placeholder url since we just need the transcript
                    analysis_obj = await asyncio.to_thread(reasoning_engine.generate_analysis, transcript, url)
                    
                    analysis_result['claims'] = [analysis_obj.primary_claim]
                    
                    counters = []
                    for ca in analysis_obj.counter_arguments:
                        counters.append({
                            'claim': analysis_obj.primary_claim,
                            'counter': f"({ca.type}) {ca.title}: {ca.content}",
                            'academic': ca.academic_insight,
                            'query': ca.youtube_query
                        })
                    analysis_result['counters'] = counters

                    status_label.text = 'Searching for opposing videos...'
                    progress.value = 0.90
                    
                    search_service = SearchService()
                    # We will search based on the first counter-argument's query, or fallback to the topic
                    search_query = counters[0]['query'] if counters else analysis_obj.topic
                    opposing = await search_service.search_videos(search_query, limit=3)
                    
                    # Convert to expected format for the UI
                    opposing_list = []
                    for vid in opposing:
                        opposing_list.append({
                            'title': getattr(vid, 'title', 'Untitled Video'),
                            'url': getattr(vid, 'url', '#'),
                            'score': getattr(vid, 'relevance_score', 'N/A')
                        })
                    analysis_result['opposing_videos'] = opposing_list

                    progress.value = 1.0
                    status_label.text = 'Analysis completed successfully!'
                    ui.notify('Analysis finished!', type='positive', position='top')

                    # Render results
                    with result_card:
                        result_card.clear()

                        with ui.expander('Full Transcript').classes('mb-4'):
                            ui.markdown(transcript[:3000] + ('...' if len(transcript) > 3000 else ''))

                        with ui.expander(f"Topic: {analysis_obj.topic}").classes('mb-4'):
                            ui.markdown(f"**Primary Claim:**\n{analysis_obj.primary_claim}")

                        with ui.expander('Counter-Arguments').classes('mb-4'):
                            for item in counters:
                                with ui.card().classes('bg-gray-700 mb-4 p-4 rounded-lg'):
                                    ui.markdown(f"**Claim:**\n{item['claim']}")
                                    ui.separator()
                                    ui.markdown(f"**Counter-Argument:**\n{item['counter']}")
                                    ui.separator()
                                    ui.markdown(f"**Academic / Logical Context:**\n{item['academic']}")

                        with ui.expander('Recommended Opposing Videos'):
                            if opposing:
                                for vid in opposing:
                                    title = vid.get('title', 'Untitled Video')
                                    url = vid.get('url', '#')
                                    score = vid.get('score', 'N/A')
                                    ui.markdown(f"- [{title}]({url})  \nRelevance score: **{score}**")
                            else:
                                ui.label('No strong opposing videos found with current filters.')

            except Exception as e:
                logger.exception("Analysis error")
                ui.notify(f'Error occurred: {str(e)}', type='negative', position='top')
                status_label.text = f'Status: Failed - {str(e)[:80]}...'
            finally:
                progress.visible = False

        ui.button(
            'START ANALYSIS',
            on_click=analyze_video
        ).props('push glossy color=indigo-600 size=lg').classes('mt-6 w-full max-w-xs font-bold')

        ui.separator().classes('my-8')

        ui.markdown(
            '*100% local • Ollama + Whisper • Privacy focused*  \n'
            'EchoBreaker • 2026'
        ).classes('text-center text-sm opacity-60')

ui.run(
    title='EchoBreaker - Local Echo Chamber Breaker',
    dark=True,
    reload=True,
    port=8080,
    show=True
)
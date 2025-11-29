"""
SearXNG plugin to filter search results to approved learning platforms only.

This plugin filters all search results to only return URLs from a whitelist
of educational platforms (Coursera, edX, Udacity, etc.)
"""

import logging
import typing as t
from urllib.parse import urlparse

from flask_babel import gettext

from . import Plugin, PluginInfo

if t.TYPE_CHECKING:
    import flask
    from searx.search import SearchWithPlugins
    from searx.extended_types import SXNG_Request
    from searx.plugins import PluginCfg

log = logging.getLogger("searx.plugins.learning_platform_filter")

# Approved learning platforms with credibility weights
LEARNING_PLATFORMS = {
    # General learning platforms
    'coursera.org': 5,
    'edx.org': 5,
    'udacity.com': 4,
    'futurelearn.com': 3,
    'linkedin.com': 2,
    'openclassrooms.com': 2,
    'grow.google': 4,
    'aws.amazon.com': 5,
    'deeplearning.ai': 5,
    'ocw.mit.edu': 4,
    'online.stanford.edu': 5,
    'online.hbs.edu': 5,
    'corporatefinanceinstitute.com': 4,
    'khanacademy.org': 3,
    'domestika.org': 2,
    'creativelive.com': 2,

    # Crypto/Blockchain specialized platforms
    'blockchain-council.org': 4,
    'consensys.net': 5,
    'cryptoconsortium.org': 5,
    'cointelegraph.com': 3,
    'ibm.com/training/blockchain': 5,
    'executive.mit.edu': 5,
    'unic.ac.cy': 5,
    'hyperledger.org': 5,
    'training.linuxfoundation.org': 5,
}


@t.final
class SXNGPlugin(Plugin):
    """Filter search results to approved learning platforms only."""

    id = "learning_platform_filter"

    def __init__(self, plg_cfg: "PluginCfg") -> None:
        super().__init__(plg_cfg)
        self.info = PluginInfo(
            id=self.id,
            name=gettext("Learning Platform Filter"),
            description=gettext("Filters search results to approved learning platforms only"),
            preference_section="general",
        )

    def post_search(self, request: "SXNG_Request", search: "SearchWithPlugins") -> bool:
        """
        Filter search results after they are retrieved.

        This hook is called after search engines return results but before
        they are displayed to the user.
        """
        # Get all results from the container
        all_results = list(search.result_container.main_results_map.values())

        # Filter results to only approved platforms
        approved_result_hashes = set()

        for result_hash, result in list(search.result_container.main_results_map.items()):
            # Check if result has a URL
            if not hasattr(result, 'url') or not result.url:
                continue

            url = result.url

            # Check if URL belongs to approved platform
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()

                # Check if domain matches any approved platform
                is_approved = False
                credibility_weight = 0

                for platform, weight in LEARNING_PLATFORMS.items():
                    if platform in domain:
                        is_approved = True
                        credibility_weight = weight
                        break

                if is_approved:
                    # Keep this result
                    approved_result_hashes.add(result_hash)
                    # Add credibility weight as metadata
                    if hasattr(result, 'metadata'):
                        result.metadata['credibility_weight'] = credibility_weight
                else:
                    log.debug("Filtering out non-approved platform: %s", url)

            except Exception as e:
                log.warning("Error parsing URL %s: %s", url, e)
                continue

        # Remove non-approved results from main_results_map
        original_count = len(search.result_container.main_results_map)
        hashes_to_remove = set(search.result_container.main_results_map.keys()) - approved_result_hashes

        for result_hash in hashes_to_remove:
            del search.result_container.main_results_map[result_hash]

        filtered_count = len(search.result_container.main_results_map)
        log.info("Filtered %d results down to %d approved platforms", original_count, filtered_count)

        return None

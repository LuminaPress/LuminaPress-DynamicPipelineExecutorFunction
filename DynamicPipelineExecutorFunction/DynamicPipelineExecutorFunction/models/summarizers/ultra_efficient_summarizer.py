import logging
from typing import List, Dict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import numpy as np
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import gc
from tqdm import tqdm
import mmap
import os
import tempfile
from functools import lru_cache
from array import array
from scipy.sparse import lil_matrix
import warnings


class UltraEfficientSummarizer:
    """Ultra memory-efficient text summarizer using advanced optimization techniques."""

    def __init__(self, cache_size: int = 1024):
        """
        Initialize summarizer with optimized settings.

        Args:
            cache_size: Size of LRU cache for similarity calculations
        """
        try:
            # Suppress NLTK download messages
            warnings.filterwarnings("ignore")
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(nltk.download, resource, quiet=True)
                    for resource in ["punkt", "stopwords"]
                ]
                list(tqdm(futures, desc="Loading NLTK resources"))

            self.stop_words = set(stopwords.words("english"))
            self.logger = self.setup_logger()
            self.cache_size = cache_size
            self.mem_monitor = MemoryMonitor()

            # Initialize word vectorization cache
            self.word_vectors: Dict[str, array] = {}

        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            raise

    @staticmethod
    def setup_logger() -> logging.Logger:
        """Configure optimized logging."""
        logger = logging.getLogger("UltraEfficientSummarizer")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def chunk_text_to_file(self, text: str) -> str:
        """Write large text to temporary file and return filename."""
        temp_file = tempfile.NamedTemporaryFile(mode="w+b", delete=False)
        try:
            temp_file.write(text.encode("utf-8"))
            return temp_file.name
        finally:
            temp_file.close()

    def preprocess_text_streaming(self, filename: str) -> List[str]:
        """Process text in streaming fashion using memory mapping."""
        sentences = []
        chunk_size = 1024 * 1024  # 1MB chunks

        with open(filename, "r+b") as file:
            # Memory map the file
            mm = mmap.mmap(file.fileno(), 0)
            file_size = mm.size()

            chunks = (file_size + chunk_size - 1) // chunk_size
            buffer = []

            with tqdm(total=chunks, desc="Preprocessing") as pbar:
                for i in range(0, file_size, chunk_size):
                    mm.seek(i)
                    chunk = mm.read(chunk_size).decode("utf-8", errors="ignore")

                    # Handle sentence boundaries between chunks
                    if buffer:
                        chunk = buffer.pop() + chunk

                    # Split into sentences
                    chunk_sentences = sent_tokenize(chunk)

                    # Save last potentially incomplete sentence
                    if not chunk.endswith((".", "!", "?")):
                        buffer.append(chunk_sentences.pop())

                    sentences.extend(chunk_sentences)
                    pbar.update(1)

                    # Periodic garbage collection
                    if i % (chunk_size * 10) == 0:
                        gc.collect()

            mm.close()

        return sentences

    @lru_cache(maxsize=1024)
    def get_word_vector(self, word: str) -> array:
        """Get cached word vector."""
        if word not in self.word_vectors:
            self.word_vectors[word] = array("f", [hash(word) % 100])
        return self.word_vectors[word]

    def process_sentence_batch(
        self, sentences: List[str], batch_size: int = 1000
    ) -> lil_matrix:
        """Process sentences in batches to build sparse similarity matrix."""
        n = len(sentences)
        similarity_matrix = lil_matrix((n, n))

        total_batches = (n * (n - 1)) // (2 * batch_size) + 1

        with tqdm(total=total_batches, desc="Building similarity matrix") as pbar:
            for i in range(0, n, batch_size):
                for j in range(i + batch_size, n, batch_size):
                    batch_end_i = min(i + batch_size, n)
                    batch_end_j = min(j + batch_size, n)

                    with ProcessPoolExecutor() as executor:
                        futures = [
                            executor.submit(
                                self.calculate_similarity_optimized,
                                sentences[i1],
                                sentences[j1],
                            )
                            for i1 in range(i, batch_end_i)
                            for j1 in range(j, batch_end_j)
                        ]

                        for idx, future in enumerate(futures):
                            i1 = i + idx // batch_size
                            j1 = j + idx % batch_size
                            similarity = future.result()
                            if similarity > 0.1:  # Only store significant similarities
                                similarity_matrix[i1, j1] = similarity
                                similarity_matrix[j1, i1] = similarity

                    pbar.update(1)

                    # Memory optimization
                    if self.mem_monitor.memory_critical():
                        self.mem_monitor.optimize_memory()

        return similarity_matrix.tocsr()

    def calculate_similarity_optimized(self, sent1: str, sent2: str) -> float:
        """Optimized sentence similarity calculation."""
        try:
            # Quick check for identical sentences
            if sent1 == sent2:
                return 1.0

            # Tokenize and filter words
            words1 = frozenset(
                word.lower()
                for word in word_tokenize(sent1)
                if word.isalnum() and word.lower() not in self.stop_words
            )
            words2 = frozenset(
                word.lower()
                for word in word_tokenize(sent2)
                if word.isalnum() and word.lower() not in self.stop_words
            )

            # Early return if no valid words
            if not words1 or not words2:
                return 0.0

            # Use Jaccard similarity for efficiency
            intersection = len(words1 & words2)
            union = len(words1 | words2)

            return intersection / union if union > 0 else 0.0

        except Exception:
            return 0.0

    def summarize(self, text: str, ratio: float = 0.3, min_length: int = 3) -> str:
        """Generate summary using optimized processing pipeline."""
        try:
            if not text or not text.strip():
                return ""

            with tqdm(total=5, desc="Summarization progress") as main_pbar:
                # Step 1: Write text to temporary file
                temp_filename = self.chunk_text_to_file(text)
                main_pbar.update(1)

                try:
                    # Step 2: Stream process text
                    sentences = self.preprocess_text_streaming(temp_filename)
                    if len(sentences) <= min_length:
                        return text
                    main_pbar.update(1)

                    # Step 3: Build similarity matrix in batches
                    similarity_matrix = self.process_sentence_batch(sentences)
                    main_pbar.update(1)

                    # Step 4: PageRank calculation
                    with tqdm(total=1, desc="Computing PageRank") as pr_pbar:
                        nx_graph = nx.from_scipy_sparse_array(similarity_matrix)
                        scores = nx.pagerank(
                            nx_graph, max_iter=100, tol=1e-4, weight="weight"
                        )
                        pr_pbar.update(1)
                    main_pbar.update(1)

                    # Step 5: Extract summary
                    num_sentences = max(min_length, int(len(sentences) * ratio))
                    ranked_sentences = sorted(
                        [(idx, score) for idx, score in scores.items()],
                        key=lambda x: x[1],
                        reverse=True,
                    )[:num_sentences]

                    summary = " ".join(
                        sentences[idx] for idx, _ in sorted(ranked_sentences)
                    )
                    main_pbar.update(1)

                    return summary

                finally:
                    # Cleanup
                    try:
                        os.unlink(temp_filename)
                    except:
                        pass

        except Exception as e:
            self.logger.error(f"Summarization error: {e}")
            return "Error during summarization. Please try again with smaller input."
        finally:
            self.mem_monitor.optimize_memory()

import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.Tokenizer;
import org.apache.lucene.analysis.miscellaneous.WordDelimiterFilter;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.lucene.analysis.tokenattributes.OffsetAttribute;
import org.apache.lucene.util.Version;

public class OptionNameAnalyzer extends Analyzer {

	private final Version matchVersion;

	public OptionNameAnalyzer(Version matchVersion) {
		this.matchVersion = matchVersion;
	}

	@Override
	protected TokenStreamComponents createComponents(String fieldName,
			Reader reader) {
		Tokenizer source = new OptionNameTokenizer(matchVersion, reader);

		TokenStream stream = source;
		stream = new WordDelimiterFilter(stream,
				WordDelimiterFilter.CATENATE_WORDS
						| WordDelimiterFilter.GENERATE_WORD_PARTS
						| WordDelimiterFilter.PRESERVE_ORIGINAL
						| WordDelimiterFilter.GENERATE_NUMBER_PARTS
						| WordDelimiterFilter.SPLIT_ON_CASE_CHANGE
						| WordDelimiterFilter.STEM_ENGLISH_POSSESSIVE, null);
		return new TokenStreamComponents(source, stream);
	}

	public static void main(String[] args) throws IOException {
		// text to tokenize
		final String text = "mapred.reduce.parallel.copies";

		Version matchVersion = Version.LUCENE_47; // Substitute desired Lucene version for XY
		OptionNameAnalyzer analyzer = new OptionNameAnalyzer(matchVersion);
		TokenStream stream = analyzer.tokenStream("field", new StringReader(text));

		// get the CharTermAttribute from the TokenStream
		CharTermAttribute termAtt = stream.addAttribute(CharTermAttribute.class);
		OffsetAttribute offsetAtt = stream.addAttribute(OffsetAttribute.class);
		try {
			stream.reset();

			// print all tokens until stream is exhausted
			while (stream.incrementToken()) {
				System.out.println(termAtt.toString());
				System.out.println("token start offset: " + offsetAtt.startOffset());
				// System.out.println("  token end offset: " + // offsetAtt.endOffset());
			}
			stream.end();

		} finally {
			stream.close();
		}
	}
}

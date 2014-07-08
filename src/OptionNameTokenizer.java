import java.io.Reader;
import org.apache.lucene.analysis.util.CharTokenizer;
import org.apache.lucene.util.Version;

public class OptionNameTokenizer extends CharTokenizer {

	public OptionNameTokenizer(Version matchVersion, Reader in) {
		super(matchVersion, in);
	}

	protected boolean isTokenChar(int arg0) {
		return ! (arg0=='.' || arg0=='_' || arg0==' ');
	}
}

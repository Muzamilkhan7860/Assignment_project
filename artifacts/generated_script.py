# Spyware Detection with AI - Sample Code

```python
import os
import hashlib
import pefile
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

class SpywareDetector:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.features = []
        self.labels = []
        
    def extract_features(self, file_path):
        """Extract features from executable files"""
        features = []
        
        try:
            # File size
            file_size = os.path.getsize(file_path)
            features.append(file_size)
            
            # PE file characteristics
            pe = pefile.PE(file_path)
            
            # Number of sections
            features.append(len(pe.sections))
            
            # Entry point address
            features.append(pe.OPTIONAL_HEADER.AddressOfEntryPoint)
            
            # Imports count
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                features.append(len(pe.DIRECTORY_ENTRY_IMPORT))
            else:
                features.append(0)
                
            # Exports count
            if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
                features.append(len(pe.DIRECTORY_ENTRY_EXPORT.symbols))
            else:
                features.append(0)
                
            # Suspicious API calls (simplified)
            suspicious_apis = ['ReadProcessMemory', 'WriteProcessMemory', 'SetWindowsHook', 
                             'Keybd_event', 'GetAsyncKeyState', 'CreateRemoteThread']
            api_count = 0
            
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for imp in entry.imports:
                        if imp.name and imp.name.decode() in suspicious_apis:
                            api_count += 1
            features.append(api_count)
            
            # Section characteristics
            executable_sections = 0
            for section in pe.sections:
                if section.Characteristics & 0x20000000:  # EXECUTE flag
                    executable_sections += 1
            features.append(executable_sections)
            
        except Exception as e:
            # If we can't parse as PE file, return None
            return None
            
        return features
    
    def train_model(self, X, y):
        """Train the AI model"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print(f"Model trained with accuracy: {accuracy:.2f}")
    
    def scan_file(self, file_path):
        """Scan a file for spyware characteristics"""
        features = self.extract_features(file_path)
        if features is None:
            return "Unknown (not a valid PE file)"
        
        prediction = self.model.predict([features])
        probability = self.model.predict_proba([features])[0][1]
        
        if prediction[0] == 1:
            return f"Spyware detected (confidence: {probability:.2%})"
        else:
            return f"Clean (confidence: {1-probability:.2%})"

# Sample usage
if __name__ == "__main__":
    print("Spyware Detection with AI")
    print("-------------------------")
    
    # Initialize detector
    detector = SpywareDetector()
    
    # Simulate training data (in real world, you'd have a dataset of known spyware/clean files)
    print("\nGenerating simulated training data...")
    num_samples = 1000
    
    # Generate some random features for clean files
    clean_files = []
    for _ in range(num_samples // 2):
        clean_files.append([
            np.random.randint(10000, 500000),  # File size
            np.random.randint(3, 10),          # Sections
            np.random.randint(0x1000, 0x5000), # Entry point
            np.random.randint(5, 30),          # Imports
            np.random.randint(0, 5),           # Exports
            np.random.randint(0, 2),           # Suspicious APIs
            np.random.randint(1, 3)            # Executable sections
        ])
    
    # Generate some random features for spyware files (with different distributions)
    spyware_files = []
    for _ in range(num_samples // 2):
        spyware_files.append([
            np.random.randint(50000, 1000000),  # File size
            np.random.randint(1, 5),            # Sections
            np.random.randint(0x5000, 0x10000), # Entry point
            np.random.randint(10, 50),          # Imports
            np.random.randint(0, 2),            # Exports
            np.random.randint(3, 10),           # Suspicious APIs
            np.random.randint(2, 5)             # Executable sections
        ])
    
    # Combine and label data
    X = clean_files + spyware_files
    y = [0] * len(clean_files) + [1] * len(spyware_files)
    
    # Train the model
    print("Training AI model...")
    detector.train_model(X, y)
    
    # Test with some sample files (in real world, you'd scan actual files)
    print("\nTesting detection:")
    test_files = [
        ("Clean sample", [
            250000,  # File size
            6,       # Sections
            0x3000,  # Entry point
            15,      # Imports
            2,       # Exports
            1,       # Suspicious APIs
            2        # Executable sections
        ]),
        ("Spyware sample", [
            750000,  # File size
            3,       # Sections
            0x8000,  # Entry point
            35,      # Imports
            0,       # Exports
            7,       # Suspicious APIs
            4        # Executable sections
        ])
    ]
    
    for name, features in test_files:
        prediction = detector.model.predict([features])
        probability = detector.model.predict_proba([features])[0][1]
        print(f"{name}: {'Spyware' if prediction[0] == 1 else 'Clean'} (confidence: {probability:.2%})")
```

This script demonstrates a basic AI approach to detect spyware by analyzing PE (Portable Executable) file characteristics. The code includes:

1. Feature extraction from executable files (size, sections, imports, etc.)
2. A Random Forest classifier for detection
3. Simulated training data (in a real scenario you'd use actual malware samples)
4. Sample detection of test cases

To use this in a real environment:
1. Replace the simulated training data with actual malware/benign samples
2. Extract features from real PE files
3. Train the model on this real data
4. Use the trained model to scan new files

Note: This is a simplified example. Real-world spyware detection requires more sophisticated features, larger datasets, and additional techniques like behavior analysis.
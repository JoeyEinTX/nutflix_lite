"""
AI utilities for lightweight image classification using pretrained models.

This module provides utilities for real-time image classification on camera frames,
designed to work with OpenCV BGR frames and integrate with the nutflix_common logging system.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Any
import os
import warnings

try:
    import torch
    import torchvision.transforms as transforms
    from torchvision import models
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

from .logger import get_logger

# Get logger for AI subsystem
logger = get_logger("ai")

# ImageNet class labels (top 10 common classes for demo)
IMAGENET_LABELS = {
    0: 'tench',
    1: 'goldfish', 
    2: 'great white shark',
    3: 'tiger shark',
    4: 'hammerhead',
    281: 'tabby cat',
    285: 'Egyptian cat',
    287: 'lynx',
    291: 'lion',
    292: 'tiger',
    # Add more as needed - this is a simplified subset
}

# Common object classes for quick demo
DEMO_LABELS = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
    'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
    'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
    'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket'
]


class ImageClassifier:
    """Lightweight image classifier for real-time camera applications."""
    
    def __init__(self, model_type: str = "torch", device: str = "auto"):
        """
        Initialize the image classifier.
        
        Args:
            model_type: "torch" for PyTorch MobileNet or "tf" for TensorFlow
            device: "cpu", "cuda", or "auto" for automatic selection
        """
        self.model = None
        self.model_type = model_type
        self.device = self._get_device(device)
        self.transform = None
        self.labels = IMAGENET_LABELS
        
        logger.info(f"Initializing ImageClassifier with model_type='{model_type}', device='{self.device}'")
        
    def _get_device(self, device: str) -> str:
        """Determine the best device to use."""
        if device == "auto":
            if TORCH_AVAILABLE and torch.cuda.is_available():
                return "cuda"
            return "cpu"
        return device
        
    def load_model(self) -> bool:
        """
        Load the pretrained model.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            if self.model_type == "torch" and TORCH_AVAILABLE:
                return self._load_torch_model()
            elif self.model_type == "tf" and TF_AVAILABLE:
                return self._load_tf_model()
            else:
                logger.error(f"Model type '{self.model_type}' not supported or dependencies not available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
            
    def _load_torch_model(self) -> bool:
        """Load PyTorch MobileNetV2 model."""
        try:
            logger.info("Loading PyTorch MobileNetV2 model...")
            
            # Suppress download warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model = models.mobilenet_v2(pretrained=True)
            
            self.model.eval()
            
            if self.device == "cuda":
                self.model = self.model.cuda()
                
            # Define transforms for preprocessing
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(224),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            logger.info("PyTorch MobileNetV2 model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load PyTorch model: {e}")
            return False
            
    def _load_tf_model(self) -> bool:
        """Load TensorFlow MobileNetV2 model."""
        try:
            logger.info("Loading TensorFlow MobileNetV2 model...")
            
            self.model = tf.keras.applications.MobileNetV2(
                weights='imagenet',
                include_top=True,
                input_shape=(224, 224, 3)
            )
            
            logger.info("TensorFlow MobileNetV2 model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load TensorFlow model: {e}")
            return False
            
    def classify_frame(self, frame: np.ndarray) -> Tuple[str, float]:
        """
        Classify a single frame from OpenCV camera.
        
        Args:
            frame: OpenCV BGR frame as numpy array
            
        Returns:
            Tuple of (class_label, confidence_score)
        """
        if self.model is None:
            logger.warning("Model not loaded, attempting to load...")
            if not self.load_model():
                return "error", 0.0
                
        try:
            if self.model_type == "torch":
                return self._classify_torch(frame)
            elif self.model_type == "tf":
                return self._classify_tf(frame)
            else:
                logger.error(f"Unknown model type: {self.model_type}")
                return "error", 0.0
                
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return "error", 0.0
            
    def _classify_torch(self, frame: np.ndarray) -> Tuple[str, float]:
        """Classify using PyTorch model."""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Apply transforms
        input_tensor = self.transform(rgb_frame).unsqueeze(0)
        
        if self.device == "cuda":
            input_tensor = input_tensor.cuda()
            
        # Run inference
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
        # Get top prediction
        top_prob, top_class = torch.topk(probabilities, 1)
        confidence = top_prob.item()
        class_idx = top_class.item()
        
        # Map to label (simplified mapping)
        if class_idx < len(self.labels):
            label = self.labels[class_idx]
        else:
            label = f"class_{class_idx}"
            
        return label, confidence
        
    def _classify_tf(self, frame: np.ndarray) -> Tuple[str, float]:
        """Classify using TensorFlow model."""
        # Convert BGR to RGB and resize
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb_frame, (224, 224))
        
        # Normalize and add batch dimension
        normalized = tf.cast(resized, tf.float32) / 255.0
        input_tensor = tf.expand_dims(normalized, 0)
        
        # Run inference
        predictions = self.model(input_tensor)
        
        # Get top prediction
        top_class = tf.argmax(predictions[0]).numpy()
        confidence = tf.reduce_max(predictions[0]).numpy()
        
        # Map to label (simplified mapping)
        if top_class < len(self.labels):
            label = self.labels[top_class]
        else:
            label = f"class_{top_class}"
            
        return label, float(confidence)


def load_model(model_type: str = "torch", device: str = "auto") -> Optional[ImageClassifier]:
    """
    Load and return an image classification model.
    
    Args:
        model_type: "torch" or "tf"
        device: "cpu", "cuda", or "auto"
        
    Returns:
        ImageClassifier instance or None if loading failed
    """
    classifier = ImageClassifier(model_type=model_type, device=device)
    
    if classifier.load_model():
        logger.info(f"Successfully loaded {model_type} classifier")
        return classifier
    else:
        logger.error(f"Failed to load {model_type} classifier")
        return None


def classify_frame(model: ImageClassifier, frame: np.ndarray) -> Tuple[str, float]:
    """
    Classify a single frame using the provided model.
    
    Args:
        model: Loaded ImageClassifier instance
        frame: OpenCV BGR frame as numpy array
        
    Returns:
        Tuple of (class_label, confidence_score)
    """
    if model is None:
        logger.error("Model is None, cannot classify frame")
        return "error", 0.0
        
    return model.classify_frame(frame)


def main():
    """Test the AI utilities with a synthetic frame."""
    logger.info("Testing AI utilities...")
    
    # Create a test frame (blue rectangle)
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    test_frame[:, :, 0] = 255  # Blue channel
    
    # Test PyTorch classifier if available
    if TORCH_AVAILABLE:
        logger.info("Testing PyTorch classifier...")
        torch_classifier = load_model("torch")
        if torch_classifier:
            label, confidence = classify_frame(torch_classifier, test_frame)
            logger.info(f"PyTorch classification: {label} (confidence: {confidence:.3f})")
    else:
        logger.info("PyTorch not available, skipping PyTorch test")
    
    # Test TensorFlow classifier if available
    if TF_AVAILABLE:
        logger.info("Testing TensorFlow classifier...")
        tf_classifier = load_model("tf")
        if tf_classifier:
            label, confidence = classify_frame(tf_classifier, test_frame)
            logger.info(f"TensorFlow classification: {label} (confidence: {confidence:.3f})")
    else:
        logger.info("TensorFlow not available, skipping TensorFlow test")
    
    # Report available dependencies
    logger.info("Dependency status:")
    logger.info(f"  PyTorch: {'✅' if TORCH_AVAILABLE else '❌'}")
    logger.info(f"  TensorFlow: {'✅' if TF_AVAILABLE else '❌'}")
    
    logger.info("AI utilities test completed")


if __name__ == "__main__":
    main()

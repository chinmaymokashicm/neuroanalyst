"""
Base classes for language encoders and decoders.

This module provides abstract base classes that define the interface
for encoding NeuProcessLogic objects to code and decoding code back
to NeuProcessLogic objects for different programming languages.
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, List, Dict, Any
from pathlib import Path

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from ...core import NeuProcessLogic, ProgrammingLanguage


class BaseEncoderConfig(BaseModel):
    """Base configuration for language encoders with enhanced validation."""
    
    model_config = ConfigDict(
        extra='forbid',  # Forbid extra fields not defined in the model
        validate_assignment=True,  # Validate when assigning to fields
        use_enum_values=True,  # Use enum values in serialization
        frozen=False  # Allow mutation for configuration updates
    )
    
    include_docstring: bool = Field(
        default=True, 
        description="Whether to include docstring in generated code"
    )
    include_comments: bool = Field(
        default=True, 
        description="Whether to include inline comments"
    )
    validate_output: bool = Field(
        default=True,
        description="Whether to validate generated code"
    )
    
    @field_validator('include_docstring', 'include_comments', 'validate_output')
    @classmethod
    def validate_boolean_fields(cls, v):
        if not isinstance(v, bool):
            raise ValueError("Field must be a boolean value")
        return v


class BaseDecoderConfig(BaseModel):
    """Base configuration for language decoders with enhanced validation."""
    
    model_config = ConfigDict(
        extra='forbid',
        validate_assignment=True,
        use_enum_values=True,
        frozen=False
    )
    
    extract_metadata: bool = Field(
        default=True, 
        description="Whether to extract metadata from code/comments"
    )
    strict_parsing: bool = Field(
        default=True, 
        description="Whether to use strict parsing"
    )
    fallback_on_error: bool = Field(
        default=False,
        description="Whether to use fallback parsing when strict parsing fails"
    )
    confidence_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for accepting parsed results"
    )
    
    @field_validator('extract_metadata', 'strict_parsing', 'fallback_on_error')
    @classmethod
    def validate_boolean_fields(cls, v):
        if not isinstance(v, bool):
            raise ValueError("Field must be a boolean value")
        return v


class CodeGenerationResult(BaseModel):
    """Enhanced result model for code generation with validation and metadata."""
    
    model_config = ConfigDict(extra='forbid', validate_assignment=True)
    
    code: str = Field(..., description="Generated code")
    language: ProgrammingLanguage = Field(..., description="Target programming language")
    imports: List[str] = Field(default_factory=list, description="Required import statements")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors if any")
    generation_time: Optional[float] = Field(None, description="Time taken to generate code in seconds")
    
    @field_validator('code')
    @classmethod
    def validate_code_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Generated code cannot be empty")
        return v
    
    @property
    def is_valid(self) -> bool:
        """Check if the generation result is valid."""
        return len(self.validation_errors) == 0
    
    def add_validation_error(self, error: str) -> None:
        """Add a validation error to the result."""
        if error not in self.validation_errors:
            self.validation_errors.append(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump()


class CodeDecodingResult(BaseModel):
    """Enhanced result model for code decoding with validation and metadata."""
    
    model_config = ConfigDict(extra='forbid', validate_assignment=True)
    
    logic: NeuProcessLogic = Field(..., description="Decoded NeuProcessLogic object")
    source_language: ProgrammingLanguage = Field(..., description="Source programming language")
    extracted_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata extracted from source")
    parsing_warnings: List[str] = Field(default_factory=list, description="Warnings during parsing")
    confidence_score: float = Field(
        default=1.0, 
        ge=0.0, 
        le=1.0, 
        description="Confidence in the decoding result"
    )
    parsing_time: Optional[float] = Field(None, description="Time taken to parse code in seconds")
    
    def add_warning(self, warning: str) -> None:
        """Add a parsing warning."""
        if warning not in self.parsing_warnings:
            self.parsing_warnings.append(warning)
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if the result has high confidence."""
        return self.confidence_score >= 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump()


class BaseEncoder(BaseModel, ABC):
    """Abstract base class for language encoders with enhanced Pydantic integration."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    language: ProgrammingLanguage = Field(..., description="Programming language this encoder supports")
    config: BaseEncoderConfig = Field(..., description="Encoder configuration")
    
    @abstractmethod
    def encode(self, logic: NeuProcessLogic) -> CodeGenerationResult:
        """
        Encode a NeuProcessLogic object into executable code.
        
        Args:
            logic: The NeuProcessLogic object to encode
            
        Returns:
            CodeGenerationResult with generated code and metadata
            
        Raises:
            ValueError: If the logic cannot be encoded
        """
        pass
    
    def validate_logic(self, logic: NeuProcessLogic) -> tuple[bool, List[str]]:
        """
        Validate that the logic can be encoded for this language.
        
        Args:
            logic: The NeuProcessLogic object to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Use Pydantic validation
        try:
            logic.model_validate(logic.model_dump())
        except Exception as e:
            errors.append(f"Pydantic validation failed: {str(e)}")
        
        # Language validation
        if logic.language != self.language:
            errors.append(f"Language mismatch: expected {self.language}, got {logic.language}")
        
        # Function name validation
        if not logic.about.name or not logic.about.name.strip():
            errors.append("Function name cannot be empty")
        
        # Code validation
        if not logic.code or not logic.code.strip():
            errors.append("Code cannot be empty")
        
        return len(errors) == 0, errors


class BaseDecoder(BaseModel, ABC):
    """Abstract base class for language decoders with enhanced Pydantic integration."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    language: ProgrammingLanguage = Field(..., description="Programming language this decoder supports")
    config: BaseDecoderConfig = Field(..., description="Decoder configuration")
    
    @abstractmethod
    def decode_from_string(self, code: str, function_name: Optional[str] = None) -> CodeDecodingResult:
        """
        Decode code string into a NeuProcessLogic object.
        
        Args:
            code: Source code containing the function
            function_name: Specific function name to extract (if multiple functions exist)
            
        Returns:
            CodeDecodingResult with decoded logic and metadata
            
        Raises:
            ValueError: If the code cannot be decoded
        """
        pass
    
    def decode_from_file(self, file_path: Union[str, Path], 
                        function_name: Optional[str] = None) -> CodeDecodingResult:
        """
        Decode code from file into a NeuProcessLogic object.
        
        Args:
            file_path: Path to the source code file
            function_name: Specific function name to extract
            
        Returns:
            CodeDecodingResult with decoded logic and metadata
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        result = self.decode_from_string(code, function_name)
        result.extracted_metadata['source_file'] = str(path.absolute())
        return result
    
    def validate_code(self, code: str) -> tuple[bool, List[str]]:
        """
        Validate that the code can be decoded.
        
        Args:
            code: Source code to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not code or not code.strip():
            errors.append("Code cannot be empty")
        
        return len(errors) == 0, errors


class LanguageCodecRegistry(BaseModel):
    """Registry for language encoders and decoders with Pydantic validation."""
    
    model_config = ConfigDict(extra='forbid', validate_assignment=True)
    
    encoders: Dict[ProgrammingLanguage, type[BaseEncoder]] = Field(
        default_factory=dict,
        description="Registered encoder classes by language"
    )
    decoders: Dict[ProgrammingLanguage, type[BaseDecoder]] = Field(
        default_factory=dict,
        description="Registered decoder classes by language"
    )
    
    def register_encoder(self, language: ProgrammingLanguage, encoder_class: type[BaseEncoder]) -> None:
        """Register an encoder for a programming language with validation."""
        if not issubclass(encoder_class, BaseEncoder):
            raise TypeError(f"Encoder must be a subclass of BaseEncoder, got {encoder_class}")
        self.encoders[language] = encoder_class
    
    def register_decoder(self, language: ProgrammingLanguage, decoder_class: type[BaseDecoder]) -> None:
        """Register a decoder for a programming language with validation."""
        if not issubclass(decoder_class, BaseDecoder):
            raise TypeError(f"Decoder must be a subclass of BaseDecoder, got {decoder_class}")
        self.decoders[language] = decoder_class
    
    def get_encoder(self, language: ProgrammingLanguage) -> Optional[type[BaseEncoder]]:
        """Get encoder class for a programming language."""
        return self.encoders.get(language)
    
    def get_decoder(self, language: ProgrammingLanguage) -> Optional[type[BaseDecoder]]:
        """Get decoder class for a programming language."""
        return self.decoders.get(language)
    
    def supported_languages(self) -> List[ProgrammingLanguage]:
        """Get list of supported programming languages."""
        return list(set(self.encoders.keys()) | set(self.decoders.keys()))
    
    def create_encoder(self, language: ProgrammingLanguage, 
                      config: Optional[BaseEncoderConfig] = None) -> BaseEncoder:
        """Create an encoder instance for a programming language with validation."""
        encoder_class = self.get_encoder(language)
        if not encoder_class:
            available = list(self.encoders.keys())
            raise ValueError(f"No encoder registered for language: {language}. Available: {available}")
        
        if config is None:
            config = BaseEncoderConfig()
        
        # Validate config is of correct type
        if not isinstance(config, BaseEncoderConfig):
            raise TypeError(f"Config must be BaseEncoderConfig or subclass, got {type(config)}")
        
        return encoder_class(language=language, config=config)
    
    def create_decoder(self, language: ProgrammingLanguage, 
                      config: Optional[BaseDecoderConfig] = None) -> BaseDecoder:
        """Create a decoder instance for a programming language with validation."""
        decoder_class = self.get_decoder(language)
        if not decoder_class:
            available = list(self.decoders.keys())
            raise ValueError(f"No decoder registered for language: {language}. Available: {available}")
        
        if config is None:
            config = BaseDecoderConfig()
        
        # Validate config is of correct type
        if not isinstance(config, BaseDecoderConfig):
            raise TypeError(f"Config must be BaseDecoderConfig or subclass, got {type(config)}")
        
        return decoder_class(language=language, config=config)
    
    def is_language_supported(self, language: ProgrammingLanguage, 
                             require_both: bool = False) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language: Programming language to check
            require_both: If True, require both encoder and decoder
            
        Returns:
            True if language is supported
        """
        has_encoder = language in self.encoders
        has_decoder = language in self.decoders
        
        if require_both:
            return has_encoder and has_decoder
        else:
            return has_encoder or has_decoder
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the registry."""
        return {
            'total_languages': len(self.supported_languages()),
            'encoders_count': len(self.encoders),
            'decoders_count': len(self.decoders),
            'languages_with_both': len([
                lang for lang in self.supported_languages() 
                if self.is_language_supported(lang, require_both=True)
            ]),
            'supported_languages': [lang.value for lang in self.supported_languages()]
        }


# Global registry instance
registry = LanguageCodecRegistry()

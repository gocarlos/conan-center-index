import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class SentryNativeConan(ConanFile):
    name = "sentry-native"
    description = "Sentry SDK for C, C++ and native applications."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getsentry/sentry-native"
    license = "MIT"
    topics = ("conan", "breakpad", "crashpad",
              "error-reporting", "crash-reporting")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backend": ["none", "crashpad", "inproc"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backend": "none"
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _cmake = None

    def requirements(self):
        self.requires("libcurl/7.68.0")
        if self.options.backend == "crashpad":
            raise ConanInvalidConfiguration("crashpad not available yet in CCI")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SENTRY_BACKEND"] = self.options.backend        

        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["sentry"]
        if self.settings.os in ("Android", "Windows"):
            self.cpp_info.exelinkflags= ["--build-id=sha1"]
            self.cpp_info.sharedlinkflags = ["--build-id=sha1"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "dl"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winhttp"]

        if not self.options.shared:
            self.cpp_info.defines = ["SENTRY_BUILD_STATIC"]

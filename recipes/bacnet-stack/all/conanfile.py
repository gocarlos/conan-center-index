import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class BacnetStackConan(ConanFile):
    name = "bacnet-stack"
    license = "BSD"
    url = "https://github.com/bacnet-stack/bacnet-stack/"
    description = """
        BACnet Protocol Stack library provides a BACnet application layer,
        network layer and media access (MAC) layer communications services."""
    topics = ("bacnet")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BACNET_STACK_BUILD_APPS"] = False
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst='licenses', src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder,
                                 "lib", "bacnet-stack", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if tools.os_info.is_linux:
            self.cpp_info.libs.append("pthread")
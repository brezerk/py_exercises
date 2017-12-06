# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

define venv
	(. .venv/bin/activate && $1)
endef

define pip_install
	$(call venv,pip install -U $1)
endef

define create_venv
	if [ ! -e .venv ]; then \
		VIRTUALENV=`which virtualenv 2>/dev/null`; \
		if [ -z "$${VIRTUALENV}" ]; then \
			echo "Virtualenv not found. Install it at first."; \
			exit 1; \
		fi; \
		$${VIRTUALENV} --no-site-packages .venv; \
		$(call pip_install,setuptools); \
	fi
endef

all:

dev:
	rm -rf .venv
	@$(call create_venv)
	@$(call pip_install,-r REQUIREMENTS.DEV)

prod:
	rm -rf .venv
	@$(call create_venv)
	@$(call pip_install,-r REQUIREMENTS.PROD)

.venv:
	@$(call create_venv)
	@$(call pip_install,-r REQUIREMENTS.DEV)

test: .venv
	@$(call venv,PYTHONPATH=lib nosetests)

clean:
	@./cleanup.sh

purge:
	@./cleanup.sh
	rm -rf .venv

build:
	@./build.sh


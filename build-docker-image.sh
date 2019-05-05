#!/bin/bash -e
DATE=$(date '+%Y%m%d')

# Now you can do just push using: `<image> push`
if [ "$1" == "push" ]; then
	DO_PUSH=1
fi

function build {
	FILE=$1
	IMAGE=$2
	TAG=$3
	REGISTRY=${4:-mgbi}

	if [ -z "$TAG" ]; then
		DATE_TAG=${DATE}
		LATEST_TAG=latest
	else
		DATE_TAG=${TAG}-${DATE}
		LATEST_TAG=${TAG}
	fi

	echo "Building ${IMAGE}:${LATEST_TAG} from ${FILE}"
	docker build -f ${FILE} -t ${REGISTRY}/${IMAGE}:${DATE_TAG} .
	docker tag ${REGISTRY}/${IMAGE}:${DATE_TAG} ${REGISTRY}/${IMAGE}:${LATEST_TAG}

	if [[ $DO_PUSH -eq 1 ]]; then
		docker push ${REGISTRY}/${IMAGE}:${DATE_TAG}
		docker push ${REGISTRY}/${IMAGE}:${LATEST_TAG}
	fi
}


build Dockerfile bitbucket-teamworkchat-bridge

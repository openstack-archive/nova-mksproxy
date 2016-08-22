# Save trace setting
XTRACE=$(set +o | grep xtrace)
set -o xtrace

# Nova virtual environment
if [[ ${USE_VENV} = True ]]; then
    PROJECT_VENV["nova"]=${NOVA_DIR}.venv
    NOVA_BIN_DIR=${PROJECT_VENV["nova"]}/bin
else
    NOVA_BIN_DIR=$(get_python_exec_prefix)
fi

NOVA_CONF=/etc/nova/nova.conf

NOVNC_MKS_DIR=$DEST/noVNC-mks
NOVNC_MKS_REPO=${NOVNC_MKS_REPO:-https://github.com/rgerganov/noVNC.git}
NOVNC_MKS_BRANCH=${NOVNC_MKS_BRANCH:-master}

function install_mksproxy {
    echo_summary "Installing nova-mksproxy"
    setup_develop $DEST/nova-mksproxy
    echo_summary "Installing noVNC (patched for MKS)"
    git_clone $NOVNC_MKS_REPO $NOVNC_MKS_DIR $NOVNC_MKS_BRANCH
}

function configure_mksproxy {
    echo_summary "Configuring MKS settings in nova.conf"
    MKSPROXY_URL=${MKSPROXY_URL:-"http://$SERVICE_HOST:6090/vnc_auto.html"}
    iniset $NOVA_CONF mks enabled "True"
    iniset $NOVA_CONF mks mksproxy_base_url "$MKSPROXY_URL"
}

function start_mksproxy {
    echo_summary "Starting nova-mksproxy ..."
    source $TOP_DIR/openrc
    run_process nova-mksproxy "$NOVA_BIN_DIR/nova-mksproxy --username admin --password $OS_PASSWORD --project admin --auth-url $OS_AUTH_URL --web $NOVNC_MKS_DIR"
}

# check for service enabled
if is_service_enabled nova-mksproxy; then

    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        install_mksproxy

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        configure_mksproxy

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start nova-mksproxy
        start_mksproxy
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_process n-mksproxy
    fi
fi

# Restore xtrace
$XTRACE


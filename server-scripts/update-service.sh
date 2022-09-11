#!/bin/bash
systemctl restart wg-quick@wg0.service
systemctl status wg-quick@wg0.service